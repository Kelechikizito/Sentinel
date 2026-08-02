"""
execute_transfer.py

Sentinel — the "act" building block.

Uses KeeperHub's Direct Execution API (not the workflow API) to move funds:
  1. (optional but recommended) Simulate the transfer to catch bad addresses,
     insufficient balance, or reverts before spending any gas
  2. Broadcast the real transfer, with an idempotency key so retries are safe
  3. Poll for the result and return the transaction hash

This module does NOT enforce spending limits or allowlists — that's
guardrail.py's job. This file only knows how to talk to KeeperHub. Call it
through the guardrail, not directly, once guardrail.py exists.
"""

import os
import sys
import time
import uuid
import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

KEEPERHUB_BASE_URL = "https://app.keeperhub.com/api"
KEEPERHUB_API_KEY = os.environ.get("KEEPERHUB_API_KEY")  # kh_...

SEPOLIA_CHAIN_ID = 11155111


def _headers(idempotency_key: str = None):
    if not KEEPERHUB_API_KEY:
        raise RuntimeError(
            "KEEPERHUB_API_KEY is not set. Run:\n"
            "  export KEEPERHUB_API_KEY=kh_your_key_here"
        )
    headers = {
        "Authorization": f"Bearer {KEEPERHUB_API_KEY}",
        "Content-Type": "application/json",
    }
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    return headers


# ---------------------------------------------------------------------------
# Step 1: simulate (dry run) — no signing, no broadcast, no gas spent
# ---------------------------------------------------------------------------


def simulate_transfer(
    to_address: str,
    amount: str,
    chain_id: int = SEPOLIA_CHAIN_ID,
    token_address: str = None,
) -> dict:
    """Validates the transfer against the chain without sending it.
    Returns the simulation result. Raises on a would-revert response.
    """
    payload = {
        "chainId": chain_id,
        "recipientAddress": to_address,
        "amount": amount,
        "simulate": True,
    }
    if token_address:
        payload["tokenAddress"] = token_address

    resp = requests.post(
        f"{KEEPERHUB_BASE_URL}/execute/transfer", json=payload, headers=_headers()
    )

    if resp.status_code == 400:
        body = resp.json()
        if body.get("wouldRevert"):
            raise RuntimeError(
                f"Simulation says this transfer would revert: {body.get('revertReason')}"
            )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Step 2: broadcast the real transfer
# ---------------------------------------------------------------------------


def broadcast_transfer(
    to_address: str,
    amount: str,
    chain_id: int = SEPOLIA_CHAIN_ID,
    token_address: str = None,
    idempotency_key: str = None,
) -> dict:
    """Sends the real transfer. Runs synchronously — status is 'completed' or
    'failed' by the time this returns, per KeeperHub's docs.
    """
    payload = {
        "chainId": chain_id,
        "recipientAddress": to_address,
        "amount": amount,
    }
    if token_address:
        payload["tokenAddress"] = token_address

    idempotency_key = idempotency_key or str(uuid.uuid4())

    resp = requests.post(
        f"{KEEPERHUB_BASE_URL}/execute/transfer",
        json=payload,
        headers=_headers(idempotency_key),
    )

    if resp.status_code == 403:
        raise RuntimeError(f"Blocked by org spending cap: {resp.json()}")

    resp.raise_for_status()
    return resp.json()  # {"executionId": ..., "status": "completed" | "failed"}


# ---------------------------------------------------------------------------
# Step 3: check status (useful if you ever go async, or want the tx link)
# ---------------------------------------------------------------------------


def get_execution_status(execution_id: str) -> dict:
    resp = requests.get(
        f"{KEEPERHUB_BASE_URL}/execute/{execution_id}/status", headers=_headers()
    )
    resp.raise_for_status()
    return resp.json()


def wait_for_completion(
    execution_id: str, max_attempts: int = 10, poll_seconds: float = 1.5
) -> dict:
    """Polls status until it reaches a terminal state. Usually unnecessary
    since broadcast_transfer() already runs synchronously, but kept as a
    safety net in case of a slow/async response.
    """
    for _ in range(max_attempts):
        status = get_execution_status(execution_id)
        if status.get("status") in ("completed", "failed"):
            return status
        time.sleep(poll_seconds)
    raise TimeoutError(f"Execution {execution_id} did not complete in time.")


# ---------------------------------------------------------------------------
# Main entry point: simulate then broadcast (the "safe first-write sequence")
# ---------------------------------------------------------------------------


def execute_transfer(
    to_address: str,
    amount: str,
    chain_id: int = SEPOLIA_CHAIN_ID,
    token_address: str = None,
    skip_simulate: bool = False,
) -> dict:
    """This is the function guardrail.py should call once a proposal passes.
    It simulates first (unless skip_simulate=True), then broadcasts for real.
    """
    if not skip_simulate:
        print(
            f"[1/2] Simulating transfer of {amount} to {to_address} on chain {chain_id}..."
        )
        sim = simulate_transfer(to_address, amount, chain_id, token_address)
        print(f"      Simulation OK. Estimated gas: {sim.get('gasEstimate')}")

    print(f"[2/2] Broadcasting real transfer of {amount} to {to_address}...")
    result = broadcast_transfer(to_address, amount, chain_id, token_address)

    if result.get("status") != "completed":
        # Fell back to async — poll for the real outcome.
        result = wait_for_completion(result["executionId"])

    status = get_execution_status(result["executionId"])
    print(f"      Done. Status: {status.get('status')}")
    if status.get("transactionLink"):
        print(f"      Explorer: {status['transactionLink']}")

    return status


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python execute_transfer.py <to_address> <amount_eth> [chain_id]")
        sys.exit(1)

    to_addr = sys.argv[1]
    amt = sys.argv[2]
    chain = int(sys.argv[3]) if len(sys.argv) > 3 else SEPOLIA_CHAIN_ID

    result = execute_transfer(to_addr, amt, chain)
    print("\nResult:", result)


# Result: {'executionId': '5a7r138f9vgtd7vbwwbjl', 'status': 'completed', 'type': 'transfer', 'transactionHash': '0x2a51b4dcd5a1215725472d40f8aa86da43d7e321e11558fc2fcbd5306df86f4f', 'transactionLink': 'https://sepolia.etherscan.io/tx/0x2a51b4dcd5a1215725472d40f8aa86da43d7e321e11558fc2fcbd5306df86f4f', 'result': {'gasUsed': '52698', 'success': True, 'sponsored': True, 'gasUsedUnits': '52698', 'transactionHash': '0x2a51b4dcd5a1215725472d40f8aa86da43d7e321e11558fc2fcbd5306df86f4f', 'transactionLink': 'https://sepolia.etherscan.io/tx/0x2a51b4dcd5a1215725472d40f8aa86da43d7e321e11558fc2fcbd5306df86f4f', 'effectiveGasPrice': '1138185086'}, 'error': None, 'gasUsedWei': '52698', 'gasPriceWei': '1138185086', 'estimatedCostUsd': None, 'retryCount': 0, 'network': '11155111', 'createdAt': '2026-08-02T10:37:34.642Z', 'completedAt': '2026-08-02T10:37:51.952Z'}

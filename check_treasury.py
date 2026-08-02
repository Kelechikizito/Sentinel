"""
check_treasury.py

Sentinel — Layer 1: read treasury state.

Uses KeeperHub's REST API (not the MCP/Gemini path) to:
  1. Create a one-node workflow that checks a wallet's native balance
  2. Execute it
  3. Wait for the result
  4. Compare the balance against a threshold and report the verdict

This is a standalone building block — no guardrail/execution logic here yet.
Run it directly to sanity-check that your KeeperHub API key + wallet work.
"""

import os
import sys
import time
import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

KEEPERHUB_BASE_URL = "https://app.keeperhub.com/api"
KEEPERHUB_API_KEY = os.environ.get("KEEPERHUB_API_KEY")  # kh_...

SEPOLIA_CHAIN_ID = "11155111"

# Threshold used for the "healthy vs needs top-up" decision.
# Move this into your rules.md-derived config once you wire in the guardrail.
LOW_BALANCE_THRESHOLD_ETH = 0.01


def _headers():
    if not KEEPERHUB_API_KEY:
        raise RuntimeError(
            "KEEPERHUB_API_KEY is not set. Run:\n"
            "  export KEEPERHUB_API_KEY=kh_your_key_here"
        )
    return {
        "Authorization": f"Bearer {KEEPERHUB_API_KEY}",
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# Step 1: create a one-node workflow that checks native balance
# ---------------------------------------------------------------------------


def create_balance_check_workflow(
    address: str, chain_id: str = SEPOLIA_CHAIN_ID
) -> str:
    """Creates a minimal workflow: Manual trigger -> web3/check-balance.
    Returns the new workflow's id.
    """
    payload = {
        "name": f"Sentinel balance check ({address[:6]}...{address[-4:]})",
        "nodes": [
            {
                "id": "trigger-1",
                "type": "trigger",
                "data": {
                    "label": "Manual Start",
                    "config": {"triggerType": "Manual"},
                },
            },
            {
                "id": "check-balance-1",
                "type": "action",
                "data": {
                    "label": "Get Native Balance",
                    "config": {
                        "actionType": "web3/check-balance",
                        "network": chain_id,
                        "address": address,
                    },
                },
            },
        ],
        "edges": [
            {"id": "trigger-check", "source": "trigger-1", "target": "check-balance-1"}
        ],
    }

    resp = requests.post(
        f"{KEEPERHUB_BASE_URL}/workflows/create", json=payload, headers=_headers()
    )
    resp.raise_for_status()
    workflow = resp.json()
    return workflow["id"]


# ---------------------------------------------------------------------------
# Step 2: execute the workflow
# ---------------------------------------------------------------------------


def execute_workflow(workflow_id: str) -> str:
    """Triggers the workflow. Returns the execution id."""
    resp = requests.post(
        f"{KEEPERHUB_BASE_URL}/workflows/{workflow_id}/execute",
        json={"input": {}},
        headers=_headers(),
    )
    resp.raise_for_status()
    return resp.json()["executionId"]


# ---------------------------------------------------------------------------
# Step 3: wait for the result
# ---------------------------------------------------------------------------


def wait_for_execution(execution_id: str, timeout_ms: int = 30000) -> dict:
    """Blocks until the execution finishes (or the timeout elapses)."""
    resp = requests.get(
        f"{KEEPERHUB_BASE_URL}/workflows/executions/{execution_id}/wait",
        params={"timeoutMs": timeout_ms},
        headers=_headers(),
    )
    resp.raise_for_status()
    return resp.json()


def get_execution_logs(execution_id: str) -> dict:
    """Fetches per-node logs — this is where the actual balance value lives
    for a web3/check-balance step."""
    resp = requests.get(
        f"{KEEPERHUB_BASE_URL}/workflows/executions/{execution_id}/logs",
        headers=_headers(),
    )
    resp.raise_for_status()
    return resp.json()


def extract_balance(logs_response: dict) -> float:
    """Pulls the ETH balance out of the check-balance node's log output."""
    for log in logs_response.get("logs", []):
        if log.get("nodeId") == "check-balance-1":
            output = log.get("output", {})
            data = output.get("data", output)  # some read steps nest under "data"
            balance = data.get("balance")
            if balance is not None:
                return float(balance)
    raise RuntimeError("Could not find a balance value in the execution logs.")


# ---------------------------------------------------------------------------
# Step 4: interpret the result
# ---------------------------------------------------------------------------


def evaluate_treasury_state(
    balance_eth: float, threshold_eth: float = LOW_BALANCE_THRESHOLD_ETH
) -> str:
    if balance_eth < threshold_eth:
        return "needs_top_up"
    return "healthy"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def check_treasury(address: str, chain_id: str = SEPOLIA_CHAIN_ID) -> dict:
    print(f"[1/4] Creating balance-check workflow for {address} on chain {chain_id}...")
    workflow_id = create_balance_check_workflow(address, chain_id)

    print(f"[2/4] Executing workflow {workflow_id}...")
    execution_id = execute_workflow(workflow_id)

    print(f"[3/4] Waiting for execution {execution_id}...")
    result = wait_for_execution(execution_id)

    if result.get("status") != "success":
        raise RuntimeError(f"Execution did not succeed: {result}")

    logs = get_execution_logs(execution_id)
    balance = extract_balance(logs)

    verdict = evaluate_treasury_state(balance)
    print(f"[4/4] Balance: {balance} ETH -> {verdict}")

    return {
        "address": address,
        "chain_id": chain_id,
        "balance_eth": balance,
        "verdict": verdict,
        "workflow_id": workflow_id,
        "execution_id": execution_id,
    }


if __name__ == "__main__":
    wallet_address = sys.argv[1] if len(sys.argv) > 1 else None
    if not wallet_address:
        print("Usage: python check_treasury.py <wallet_address>")
        sys.exit(1)

    result = check_treasury(wallet_address)
    print("\nResult:", result)

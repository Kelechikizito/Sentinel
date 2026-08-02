"""
main.py

Sentinel — the orchestrator.

Chains the three building blocks into one real end-to-end flow:

    check_treasury()  ->  guardrail.evaluate()  ->  execute_transfer()

This is the script to run for your demo. It supports two modes:

  1. Automatic: read the treasury balance, and if it's below the
     low-balance threshold, propose a top-up transfer.
  2. Manual: pass an explicit proposal (amount + recipient) to test the
     guardrail directly — this is how you demo both the PASS and BLOCK
     paths on camera.

Usage:
  python3 main.py auto <wallet_address>
  python3 main.py propose <to_address> <amount_eth>
"""

import sys

import guardrail
from check_treasury import check_treasury, SEPOLIA_CHAIN_ID
from execute_transfer import execute_transfer


def run_proposal(
    to_address: str, amount: str, chain_id: int = SEPOLIA_CHAIN_ID
) -> dict:
    """The core pipeline: one proposal, in through the guardrail, out as
    either a blocked log entry or a real onchain transaction.
    """
    proposal = {
        "action": "execute_transfer",
        "to_address": to_address,
        "amount": amount,
        "chain_id": chain_id,
    }

    print(f"\nProposal: transfer {amount} ETH to {to_address}")
    verdict, reason = guardrail.evaluate(proposal)

    if verdict == "BLOCK":
        print(f"BLOCKED — no funds moved. Reason: {reason}")
        return {
            "proposal": proposal,
            "verdict": verdict,
            "reason": reason,
            "execution": None,
        }

    print("Guardrail passed — proceeding to KeeperHub.")
    execution_result = execute_transfer(to_address, amount, chain_id)

    # Log the final outcome too, alongside the earlier PASS decision.
    guardrail.log_decision(proposal, "EXECUTED", reason, execution_result)

    return {
        "proposal": proposal,
        "verdict": verdict,
        "reason": reason,
        "execution": execution_result,
    }


def run_auto(
    wallet_address: str,
    top_up_amount: str = "0.005",
    top_up_target: str = None,
    chain_id: int = SEPOLIA_CHAIN_ID,
) -> dict:
    """Reads treasury state; if it's low, proposes a top-up transfer through
    the same guardrail pipeline. If healthy, does nothing.
    """
    state = check_treasury(wallet_address, chain_id)

    if state["verdict"] == "healthy":
        print(f"\nTreasury healthy at {state['balance_eth']} ETH. No action needed.")
        return {"treasury_state": state, "action_taken": False}

    print(f"\nTreasury low at {state['balance_eth']} ETH. Proposing a top-up.")

    if not top_up_target:
        rules = guardrail.load_rules()
        top_up_target = rules["allowlist"][0]
        print(
            f"(No target specified — using first allowlisted address: {top_up_target})"
        )

    result = run_proposal(top_up_target, top_up_amount, chain_id)
    return {"treasury_state": state, "action_taken": True, "result": result}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "auto":
        if len(sys.argv) < 3:
            print("Usage: python3 main.py auto <wallet_address>")
            sys.exit(1)
        outcome = run_auto(sys.argv[2])

    elif mode == "propose":
        if len(sys.argv) < 4:
            print("Usage: python3 main.py propose <to_address> <amount_eth>")
            sys.exit(1)
        outcome = run_proposal(sys.argv[2], sys.argv[3])

    else:
        print(__doc__)
        sys.exit(1)

    print("\n--- Final outcome ---")
    print(outcome)

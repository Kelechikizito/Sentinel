"""
guardrail.py

Sentinel — the safety layer.

Loads rules from rules.json *at check time* (not at import time), so a user
can update rules.json externally (e.g. via set_rules.py, or a future
frontend form + API) and the very next check picks up the new values —
no restart needed.

This module does NOT call KeeperHub. It only decides PASS or BLOCK.
Wire it in front of execute_transfer.py in main.py.
"""

import json
import os
from datetime import datetime, timezone

RULES_PATH = os.path.join(os.path.dirname(__file__), "rules.json")
LOG_PATH = os.path.join(os.path.dirname(__file__), "log.jsonl")


# ---------------------------------------------------------------------------
# Rules loading
# ---------------------------------------------------------------------------


def load_rules() -> dict:
    """Reads rules.json fresh every time. This is what makes rules
    'user-configurable on the fly' — no code change or restart needed to
    update limits or the allowlist.
    """
    if not os.path.exists(RULES_PATH):
        raise FileNotFoundError(
            f"rules.json not found at {RULES_PATH}. Create one, or run "
            f"set_rules.py to generate a default."
        )
    with open(RULES_PATH, "r") as f:
        return json.load(f)


def save_rules(rules: dict) -> None:
    """Persists updated rules. This is the 'server' side of the
    user-configurable pipeline — a future API endpoint would call this
    exact function after validating a frontend form submission.
    """
    with open(RULES_PATH, "w") as f:
        json.dump(rules, f, indent=2)


# ---------------------------------------------------------------------------
# The actual guardrail check — pure logic, deterministic, no network calls
# ---------------------------------------------------------------------------


def check_proposal(proposal: dict) -> tuple:
    """
    proposal is expected to look like:
      {
        "action": "execute_transfer",
        "to_address": "0x...",
        "amount": "0.001",     # string or float, human-readable ETH
        "chain_id": 11155111
      }

    Returns (verdict, reason) where verdict is "PASS" or "BLOCK".
    Checks run in a fixed order; the first failing rule is reported.
    """
    rules = load_rules()

    action = proposal.get("action")
    if action not in rules["allowed_actions"]:
        return "BLOCK", f"Action '{action}' is not an allowed action type."

    to_address = proposal.get("to_address", "")
    allowlist = [addr.lower() for addr in rules["allowlist"]]
    if to_address.lower() not in allowlist:
        return "BLOCK", f"Address {to_address} is not on the allowlist."

    try:
        amount = float(proposal.get("amount", 0))
    except (TypeError, ValueError):
        return "BLOCK", f"Amount '{proposal.get('amount')}' is not a valid number."

    if amount > rules["max_amount_eth"]:
        return "BLOCK", (
            f"Amount {amount} ETH exceeds the spending limit of "
            f"{rules['max_amount_eth']} ETH."
        )

    if amount <= 0:
        return "BLOCK", "Amount must be greater than zero."

    return "PASS", "All checks passed."


# ---------------------------------------------------------------------------
# Logging — the audit narrative alongside KeeperHub's own audit trail
# ---------------------------------------------------------------------------


def log_decision(
    proposal: dict, verdict: str, reason: str, execution_result: dict = None
) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "proposal": proposal,
        "verdict": verdict,
        "reason": reason,
        "execution_result": execution_result,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# Convenience: check + log in one call
# ---------------------------------------------------------------------------


def evaluate(proposal: dict) -> tuple:
    verdict, reason = check_proposal(proposal)
    log_decision(proposal, verdict, reason)
    print(f"[guardrail] {verdict}: {reason}")
    return verdict, reason


if __name__ == "__main__":
    # Quick manual test of a few cases when run directly.
    rules = load_rules()
    print("Loaded rules:", json.dumps(rules, indent=2))

    test_cases = [
        {
            "action": "execute_transfer",
            "to_address": rules["allowlist"][0],
            "amount": "0.001",
        },
        {
            "action": "execute_transfer",
            "to_address": rules["allowlist"][0],
            "amount": "1",
        },
        {
            "action": "execute_transfer",
            "to_address": "0x000000000000000000000000000000deadbeef",
            "amount": "0.001",
        },
        {
            "action": "execute_contract_call",
            "to_address": rules["allowlist"][0],
            "amount": "0.001",
        },
    ]

    print("\nRunning test cases:")
    for case in test_cases:
        evaluate(case)

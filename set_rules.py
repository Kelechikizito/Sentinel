"""
set_rules.py

Sentinel — the "frontend" (stand-in).

A real product would have a web form calling a backend API that writes to
a database. For the hackathon MVP, this CLI plays that same role: it lets
a user view and update the guardrail rules on the fly, and guardrail.py
picks up the change on its very next check (since it reads rules.json
fresh every time, not once at startup).

Usage:
  python3 set_rules.py show
  python3 set_rules.py set-limit 0.01
  python3 set_rules.py add-address 0xAbC123...
  python3 set_rules.py remove-address 0xAbC123...
"""

import sys
import json
from guardrail import load_rules, save_rules


def show():
    rules = load_rules()
    print(json.dumps(rules, indent=2))


def set_limit(new_limit: str):
    rules = load_rules()
    old = rules["max_amount_eth"]
    rules["max_amount_eth"] = float(new_limit)
    save_rules(rules)
    print(f"Spending limit updated: {old} ETH -> {rules['max_amount_eth']} ETH")


def add_address(address: str):
    rules = load_rules()
    if address.lower() in [a.lower() for a in rules["allowlist"]]:
        print(f"{address} is already on the allowlist.")
        return
    rules["allowlist"].append(address)
    save_rules(rules)
    print(f"Added {address} to the allowlist.")


def remove_address(address: str):
    rules = load_rules()
    before = len(rules["allowlist"])
    rules["allowlist"] = [a for a in rules["allowlist"] if a.lower() != address.lower()]
    save_rules(rules)
    if len(rules["allowlist"]) < before:
        print(f"Removed {address} from the allowlist.")
    else:
        print(f"{address} was not on the allowlist.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "show":
        show()
    elif command == "set-limit" and len(sys.argv) == 3:
        set_limit(sys.argv[2])
    elif command == "add-address" and len(sys.argv) == 3:
        add_address(sys.argv[2])
    elif command == "remove-address" and len(sys.argv) == 3:
        remove_address(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)

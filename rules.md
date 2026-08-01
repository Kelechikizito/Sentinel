## Guardrail Rules

1. Spending limit
   - Max transfer amount: 0.005 ETH (testnet)
   - If proposed amount > 0.005 ETH → BLOCK

2. Allowlist
   - Approved addresses: [0xDBC29E79b2B3b62C015AB598D0bb86681313d90F, 0x93923B42Ff4bDF533634Ea71bF626c90286D27A0]
   - If target address not in this list → BLOCK

3. Schema validity
   - Action must be "execute_transfer" (exact match from list_action_schemas)
   - If agent proposes any other/unknown action → BLOCK
   - The required fields for the execute_transfer tool are:
     - chain_id (string): The Chain ID of the target blockchain (e.g., '1' for Ethereum, '8453' for Base).
     - to_address (string): The recipient's wallet address (starting with 0x).
     - amount (string): The transfer amount in human-readable units (e.g., '0.1').
     - Optional Fields:
       - token_address (equivalent to token): The contract address of an ERC20 token. If omitted, the transfer
         defaults to native tokens (e.g., ETH, MATIC).
       - idempotency_key: An optional unique transaction key to prevent double-spending / duplicate executions
         within a 24-hour window.

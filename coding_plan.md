Tight timeline — here's a build order that gets you a working demo, not a perfect product. Cut scope ruthlessly.

## Hour 0–1: Lock the scope, don't skip this

- **Pick Aave repay only.** Sky/multi-protocol is the stretch goal you mention only if time remains — don't touch it now.
- Write down, literally in a text file: "Doer reads Aave health factor → proposes repay if below X → critique agent checks it → if approved, KeeperHub executes repay → log both agents' reasoning." That's your whole spec. Anything not in that sentence doesn't get built.

## Hour 1–3: Confirm the KeeperHub actions exist and what they need

- Using your API key, hit KeeperHub's MCP/API directly (curl or a quick script) for:
  - `search_protocol_actions` for "Aave V3" → get exact action IDs for `Get User Account Data` and `Repay Debt`, and their required params
  - Do this on testnet (Sepolia = `"11155111"`) so you're not risking real funds
- Get one successful **read** call working (health factor) before writing any agent logic. If this doesn't work early, everything else stalls — de-risk it first.

## Hour 3–6: Build the doer + critique logic (backend, plain scripts first, not UI)

- Write two functions, not agents-as-a-framework — for 24h, skip agent frameworks (CrewAI etc.), just two LLM calls:

```
proposeAction(accountData) → { asset, amount, action, reason }
critiqueAction(accountData, proposal) → { approved: bool, reason }
```

- Use Gemini free tier or your $5 Anthropic credit if it landed — whichever responds now.
- Test this in isolation (node script, console.log output) before touching your Next.js frontend at all.

## Hour 6–9: Wire in real KeeperHub execution

- If `critiqueAction` approves → call KeeperHub's `Repay Debt` action for real (testnet)
- Log every step to a simple JSON array or file: `{timestamp, step, data, reasoning}` — this is your audit trail extension, keep it dead simple
- Get **one successful real transaction** on testnet you can screenshot/link — this is a submission requirement, don't leave it to the last hour

## Hour 9–14: Connect to your existing Next.js frontend

- Don't redesign it — add one page/route that:
  - Triggers the flow (a "Run Check" button)
  - Displays: health factor → doer's proposal → critique's verdict + reasoning → execution result + tx link
- This is just displaying the JSON from your backend script — no need for anything fancy. A clean readable log view wins over a polished UI here.

## Hour 14–18: Test end-to-end, break it on purpose

- Run it a few times with different simulated health factors (mock the data if needed to trigger both approve and reject cases) — you want your demo to show the critique agent **rejecting** something at least once, that's the proof it's not a rubber stamp.
- Fix whatever breaks. Don't add features now.

## Hour 18–21: Record the demo video + write the README

- Screen record: show the health factor, the doer's proposal, the critique's reasoning, the real KeeperHub execution, the linked transaction.
- README: setup steps, architecture diagram (even a simple text one), how KeeperHub is used, what the critique agent adds.

## Hour 21–24: Buffer

- Something will break late — this buffer is non-negotiable. If everything's fine, use it to add the "generic across protocols" pitch in your write-up even if you only demoed one (be honest: say "architected to be protocol-agnostic, demoed on Aave" — don't claim untested capability as fact).

**Right now, your very next action:** get your KeeperHub API key hitting `search_protocol_actions` for Aave V3 and confirm the exact response shape. Do that before writing another line of plan — it's the one unknown that could derail everything else.

Use create_workflow with this definition, but change the network field to "11155111" for Sepolia:

{
"name": "Check Wallet Balance Workflow",
"nodes": [
{
"id": "trigger-1",
"type": "trigger",
"data": {
"label": "Manual Start",
"type": "trigger",
"config": { "triggerType": "Manual" }
}
},
{
"id": "check-balance-1",
"type": "action",
"data": {
"label": "Get Native Balance",
"type": "action",
"config": {
"actionType": "web3/check-balance",
"network": "11155111",
"address": "0xDBC29E79b2B3b62C015AB598D0bb86681313d90F"
}
}
}
],
"edges": [
{ "id": "edge-1", "source": "trigger-1", "target": "check-balance-1" }
]
}

res: Workflow Name: Check Wallet Balance Workflow

- Workflow ID: dzla7k38gveivu31yw7hy

```

Use get_execution to show the balance result
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✓  get_execution (keeperhub MCP Server) {"executionId":"8txzavnkp1jp5z9tewqhr"}                                                                     │
│                                                                                                                                                     │
│ {                                                                                                                                                   │
│   "status": {                                                                                                                                       │
│     "status": "success",                                                                                                                            │
│     "nodeStatuses": [                                                                                                                               │
│       {                                                                                                                                             │
│         "nodeId": "trigger-1",                                                                                                                      │
│         "status": "success"                                                                                                                         │
│       },                                                                                                                                            │
│       {                                                                                                                                             │
│         "nodeId": "check-balance-1",                                                                                                                │
│         "status": "success"                                                                                                                         │
│       }                                                                                                                                             │
│     ],                                                                                                                                              │
│     "progress": {                                                                                                                                   │
│       "totalSteps": 0,                                                                                                                              │
│       "completedSteps": 2,                                                                                                                          │
│       "runningSteps": 0,                                                                                                                            │
│       "currentNodeId": null,                                                                                                                        │
│       "currentNodeName": null,                                                                                                                      │
│       "percentage": 0                                                                                                                               │
│     },                                                                                                                                              │
│     "errorContext": null,                                                                                                                           │
│     "transactionHashes": []                                                                                                                         │
│   },                                                                                                                                                │
│   "logs": {                                                                                                                                         │
│     "execution": {                                                                                                                                  │
│       "id": "8txzavnkp1jp5z9tewqhr",                                                                                                                │
│       "workflowId": "dzla7k38gveivu31yw7hy",                                                                                                        │
│       "userId": "tfnbmNRqXojF2AyJSlOGH9czKDEPEXQU",                                                                                                 │
│       "status": "success",                                                                                                                          │
│       "input": {},                                                                                                                                  │
│       "output": {                                                                                                                                   │
│         "address": "0xDBC29E79b2B3b62C015AB598D0bb86681313d90F",                                                                                    │
│         "balance": "0.682162204616387892",                                                                                                          │
│         "success": true,                                                                                                                            │
│         "balanceWei": "682162204616387892",                                                                                                         │
│         "addressLink": "https://sepolia.etherscan.io/address/0xDBC29E79b2B3b62C015AB598D0bb86681313d90F"                                            │
│       },                                                                                                                                            │
│       "error": null,                                                                                                                                │
│       "errorCategory": null,                                                                                                                        │
│       "errorType": null,                                                                                                                            │
│       "errorCode": null,                                                                                                                            │
│       "startedAt": "2026-08-01T17:16:25.637Z",                                                                                                      │
│       "completedAt": "2026-08-01T17:16:26.027Z",                                                                                                    │
│       "duration": "342",                                                                                                                            │
│       "totalSteps": null,                                                                                                                           │
│       "completedSteps": "2",                                                                                                                        │
│       "currentNodeId": null,                                                                                                                        │
│       "currentNodeName": null,                                                                                                                      │
│       "lastSuccessfulNodeId": "check-balance-1",                                                                                                    │
│       "lastSuccessfulNodeName": "Get Native Balance",                                                                                               │
│       "executionTrace": [                                                                                                                           │
│         "trigger-1",                                                                                                                                │
│         "check-balance-1"                                                                                                                           │
│       ],                                                                                                                                            │
│       "runId": "wrun_01KYZ57E5JKS1RRZ48Q4YQ37WS",                                                                                                   │
│       "transactionHashes": [],                                                                                                                      │
│       "gasUsedWei": null,                                                                                                                           │
│       "billable": true,                                                                                                                             │
│       "triggeredByUserApiKeyId": null,                                                                                                              │
│       "triggeredByOrgApiKeyId": "9iou4ab5a7wmos36bftyf",                                                                                            │
│       "triggeredByIp": null,                                                                                                                        │
│       "triggeredByCountry": null,                                                                                                                   │
│       "triggerSource": "manual",                                                                                                                    │
│       "triggeredByCredentialType": "org_api_key",                                                                                                   │
│       "triggeredByCredentialLabel": null,                                                                                                           │
│       "executedWorkflowHash": "fa09490913b157ca0c1c3831b42e3db5984acde8d640b801f43241a7a8652394",                                                   │
│       "dispatchKey": null,                                                                                                                          │
│       "deletedAt": null,                                                                                                                            │
│       "workflow": {                                                                                                                                 │
│         "id": "dzla7k38gveivu31yw7hy",                                                                                                              │
│         "name": "Check Wallet Balance Workflow",                                                                                                    │
│         "description": null,                                                                                                                        │
│         "userId": "tfnbmNRqXojF2AyJSlOGH9czKDEPEXQU",                                                                                               │
│         "organizationId": "b9004e18-a2cc-4be1-a48d-d64f73858288",                                                                                   │
│         "isAnonymous": false,                                                                                                                       │
│         "featured": false,                                                                                                                          │
│         "featuredOrder": 0,                                                                                                                         │
│         "featuredProtocol": null,                                                                                                                   │
│         "featuredProtocolOrder": 0,                                                                                                                 │
│         "projectId": null,                                                                                                                          │
│         "tagId": null,                                                                                                                              │
│         "nodes": [                                                                                                                                  │
│           {                                                                                                                                         │
│             "id": "trigger-1",                                                                                                                      │
│             "data": {                                                                                                                               │
│               "type": "trigger",                                                                                                                    │
│               "label": "Manual Start",                                                                                                              │
│               "config": {                                                                                                                           │
│                 "triggerType": "Manual"                                                                                                             │
│               },                                                                                                                                    │
│               "status": "idle"                                                                                                                      │
│             },                                                                                                                                      │
│             "type": "trigger",                                                                                                                      │
│             "position": {                                                                                                                           │
│               "x": 0,                                                                                                                               │
│               "y": 0                                                                                                                                │
│             }                                                                                                                                       │
│           },                                                                                                                                        │
│           {                                                                                                                                         │
│             "id": "check-balance-1",                                                                                                                │
│             "data": {                                                                                                                               │
│               "type": "action",                                                                                                                     │
│               "label": "Get Native Balance",                                                                                                        │
│               "config": {                                                                                                                           │
│                 "address": "0xDBC29E79b2B3b62C015AB598D0bb86681313d90F",                                                                            │
│                 "network": "11155111",                                                                                                              │
│                 "actionType": "web3/check-balance"                                                                                                  │
│               },                                                                                                                                    │
│               "status": "idle"                                                                                                                      │
│             },                                                                                                                                      │
│             "type": "action",                                                                                                                       │
│             "position": {                                                                                                                           │
│               "x": 252,                                                                                                                             │
│               "y": 0                                                                                                                                │
│             }                                                                                                                                       │
│           }                                                                                                                                         │
│         ],                                                                                                                                          │
│         "edges": [                                                                                                                                  │
│           {                                                                                                                                         │
│             "id": "edge-1",                                                                                                                         │
│             "source": "trigger-1",                                                                                                                  │
│             "target": "check-balance-1"                                                                                                             │
│           }                                                                                                                                         │
│         ],                                                                                                                                          │
│         "visibility": "private",                                                                                                                    │
│         "enabled": false,                                                                                                                           │
│         "sourceWorkflowId": null,                                                                                                                   │
│         "createdAt": "2026-08-01T17:14:48.024Z",                                                                                                    │
│         "updatedAt": "2026-08-01T17:14:48.024Z",                                                                                                    │
│         "seededAt": null,                                                                                                                           │
│         "isListed": false,                                                                                                                          │
│         "listedSlug": null,                                                                                                                         │
│         "listedAt": null,                                                                                                                           │
│         "inputSchema": null,                                                                                                                        │
│         "outputMapping": null,                                                                                                                      │
│         "priceUsdcPerCall": null,                                                                                                                   │
│         "workflowType": "read",                                                                                                                     │
│         "category": null,                                                                                                                           │
│         "chain": null,                                                                                                                              │
│         "listingVersion": 1,                                                                                                                        │
│         "deletedAt": null,                                                                                                                          │
│         "deactivatedAt": null                                                                                                                       │
│       }                                                                                                                                             │
│     },                                                                                                                                              │
│     "logs": [                                                                                                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

✦ The execution has completed successfully! Here is the balance result:

   * Address Checked: 0xDBC29E79b2B3b62C015AB598D0bb86681313d90F (Sepolia testnet)
   * Balance: 0.682162204616387892 ETH
   * Balance (Wei): 682162204616387892 Wei
   * Explorer Link: Sepolia Etherscan (https://sepolia.etherscan.io/address/0xDBC29E79b2B3b62C015AB598D0bb86681313d90F)


```

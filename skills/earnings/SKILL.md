---
name: bacon-earnings
description: Show Bacon earnings — balance, impressions, CPM, payout status, subscription coverage. Use when the user runs /bacon:earnings or asks about their ad revenue, balance, or how much they've earned.
---

# Bacon Earnings

Run ONE command and present the output:
`python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-earnings summary`

Show the CLI output as-is. Then:
- If balance ≥ $10: mention payout is available at geturbacon.dev/dashboard
- If balance < $1 after 7+ active days: suggest `/bacon:config` to boost frequency or profile tier

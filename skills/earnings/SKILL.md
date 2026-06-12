---
description: Show Bacon earnings — balance, impressions, CPM, payout status. Use when the user runs /bacon:earnings or asks about their ad revenue.
---

# Bacon Earnings

Run ONE command and present the output:
`python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-earnings summary`

Show the CLI output as-is. If balance ≥ $10, mention payout is available at geturbacon.dev/dashboard.
If balance < $1 after 7+ days active, suggest `/bacon:config` to boost frequency or profile.

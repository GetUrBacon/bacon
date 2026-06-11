---
description: Show Bacon earnings dashboard — balance, impressions, payout history, and estimated time to cover your AI subscription. Use when user asks about earnings, balance, or revenue.
---

# Bacon Earnings Dashboard

Show the user their current Bacon earnings and status.

## Steps

1. Run the earnings CLI (use the absolute path so it resolves in the minimal hook PATH):
   `python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-earnings summary`
   If `$CLAUDE_PLUGIN_ROOT` is unavailable, fall back to:
   `python3 /Users/oscar-rivas/Github/bacon/bin/bacon-earnings summary`
2. The CLI already prints a formatted dashboard — show its output directly. Do not reformat or invent numbers.

```
💰 ADS Earnings Dashboard
─────────────────────────────────────
Balance:          $X.XX  (pays out at $10)
This month:       $X.XX
All time:         $X.XX

Impressions today:    XXX
Impressions/month:    X,XXX

Frequency tier:   [Minimal/Standard/More/Max/Every]
Profile tier:     [Anonymous/Basic/Full]
Effective CPM:    $X.XX

─────────────────────────────────────
Claude subscription progress:
  Pro  ($20/mo):   [████░░░░░░] XX% covered
  Max  ($100/mo):  [█░░░░░░░░░] XX% covered

Next payout:      ~X days  ($X.XX remaining to threshold)
─────────────────────────────────────
```

3. If balance < $1 and they've been active > 7 days, suggest:
   "Tip: Switch to a higher frequency tier or add a developer profile to earn more. Run `/bacon:config` to adjust."

## Arguments

$ARGUMENTS can be:
- `history` — show last 30 days of daily earnings
- `payouts` — show payout transaction history

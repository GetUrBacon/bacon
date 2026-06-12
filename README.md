# Bacon — Claude Code Plugin

Get paid to code. Bacon serves the occasional clearly-labeled contextual ad alongside Claude's replies and pays you 50% of every filled impression. Your prompts never leave your machine.

## Install

The fastest way is the guided wizard:

```bash
npx @geturbacon/wizard
```

Or install the plugin directly inside Claude Code:

```
/plugin install github:GetUrBacon/bacon
```

Then run `/bacon:setup` to finish onboarding.

## Skills

| Skill | What it does |
|---|---|
| `/bacon:setup` | First-run onboarding — creates config, optionally connects account |
| `/bacon:earnings` | View balance, impression count, subscription progress |
| `/bacon:config` | Change frequency, profile tier, ad surface, blocklist |

## How it works

- Installs a `UserPromptSubmit` hook that runs on every N-th prompt (you choose)
- Runs a **local** first-price auction from a pre-fetched campaign cache — no network call in the hot path
- Winning ad is appended as `additionalContext` to the prompt, clearly labeled `💼 Sponsored:`
- Background refill keeps the local cache warm so ads are always available

## Frequency tiers

| Tier | Frequency | Est. earnings (500 prompts/day, anonymous profile) |
|---|---|---|
| Minimal | 1 per 20 | ~$0.75/mo |
| Standard | 1 per 10 | ~$1.50/mo |
| More | 1 per 5 | ~$3.00/mo |
| Max | 1 per 2 | ~$7.50/mo |
| Every | every prompt | ~$15/mo |

These are rough estimates based on a $1 anonymous CPM. Add a developer profile to unlock 2–6x higher CPM. Actual earnings depend on advertiser demand and your usage — most developers make a few dollars a month.

## Privacy

- Your prompts are **never** sent to our servers — intent is derived locally
- Default mode is fully anonymous (random UUID, no account required)
- Profile sharing is opt-in and reversible — you choose what to share
- Uninstall cleanly: `bacon-setup uninstall`

## Ad surfaces

| Surface | Where ads appear |
|---|---|
| `strip` | One-line text in Claude's replies |
| `cards` | Boxed card/banner in replies (default) |
| `statusline` | Animated statusline only — never in replies |
| `both` | Replies + statusline |

## Configuration

```bash
bacon-config show               # current settings + earnings estimate
bacon-config frequency minimal  # reduce ad frequency
bacon-config profile stack      # share language/framework for better CPM
bacon-config pause              # pause all ads
bacon-config resume             # resume
```

## Payouts

Earnings accumulate in your Bacon balance. Payouts are issued when your balance reaches the threshold — see [geturbacon.dev/dashboard](https://geturbacon.dev/dashboard) for current status.

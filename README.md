# Bacon — Claude Code Plugin

Get your bacon. Earn revenue from contextual ads while you code — your AI subscription pays for itself.

## Install

```bash
/plugin install github:geturbacon/bacon
```

Then run:

```
/bacon:setup
```

## Skills

| Skill | What it does |
|---|---|
| `/bacon:setup` | Create account, choose ad frequency, build profile |
| `/bacon:earnings` | View balance, impressions, subscription progress |
| `/bacon:config` | Change frequency tier, profile, payout method |

## How it works

- Installs a `UserPromptSubmit` hook via the plugin's `hooks/hooks.json`
- On every N-th prompt (you choose), calls the Bacon auction API (<80ms)
- Winning ad is injected as `additionalContext` — clearly labeled `💼 Sponsored:`
- You earn 50% of the impression revenue, paid weekly via Stripe

## Frequency tiers

| Tier | Frequency | Est. earnings (500 prompts/day, no profile) |
|---|---|---|
| Minimal | 1 per 20 | ~$0.75/mo |
| Standard | 1 per 10 | ~$1.50/mo |
| More | 1 per 5 | ~$3.00/mo |
| Max | 1 per 2 | ~$7.50/mo |
| Every | every prompt | ~$15/mo |

Add a developer profile to unlock 4–8x higher CPM. Max tier + full profile can cover your AI subscription.

## Privacy

- Your prompts are **never** sent to our servers
- Profile is opt-in — you choose what to share
- Anonymous UUID only — no PII collected
- Uninstall anytime: `/bacon:config uninstall`

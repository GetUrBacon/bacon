---
description: Set up Bacon — create config, choose ad preferences, optionally enable the animated statusline. Use when the user runs /bacon:setup or wants to start earning from ads.
---

# Bacon Setup

CLIs at `${CLAUDE_PLUGIN_ROOT}/bin/`:  `bacon-setup`  `bacon-config`  `bacon-earnings`

## Flow

**Step 1 — Check if already set up**
Run ONE command: `python3 <path>/bacon-setup status && python3 <path>/bacon-earnings summary`
If active, show status + offer `/bacon:config`. Stop here.

**Step 2 — Init**
`python3 <path>/bacon-setup init`

**Step 3 — Preferences (ONE AskUserQuestion call, all 4 questions at once)**
- Frequency: Minimal (~$0.75/mo) / Standard (~$1.50/mo) / More (~$3/mo) / Max (~$7.50/mo) / Every (~$15/mo)
- Personalization: Anonymous / Stack only / Full (~6.5x CPM) — prompts/code/keys NEVER shared
- Surface: Strip only / Cards+Banners / Statusline / Both
- Block categories (multi-select): crypto / food / ai / payments / infra / or Nothing

**Step 4 — Apply in ONE bash call**
Combine all config commands: `python3 <path>/bacon-config frequency <x> && python3 <path>/bacon-config profile <x> && ...`
If surface includes statusline: `python3 <path>/bacon-setup statusline-enable --style marquee`

**Step 5 — Confirm**
`python3 <path>/bacon-config show`

## Notes
- `bacon-config` writes to `~/.bacon/config.json`. If auto mode blocks it, show the command for the user to run with `!`.
- Statusline requires editing `~/.claude/settings.json` — only via `bacon-setup statusline-enable`, never directly.

## Arguments
- `statusline` → jump to statusline enable
- `uninstall` → `python3 <path>/bacon-setup uninstall` with confirmation

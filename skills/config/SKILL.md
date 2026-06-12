---
name: bacon-config
description: Configure Bacon ad settings — frequency, profile/personalization, ad surface, category blocklist, pause/resume. Use when the user runs /bacon:config or wants to change how ads appear or earn more.
---

# Bacon Config

CLI: `python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-config <command>`

## Flow

**Step 1 — Read current settings**
`python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-config show`

**Step 2 — Ask (ONE AskUserQuestion call)**
If `$ARGUMENTS` names a specific setting, show only that picker. Otherwise show all 4 at once, marking current values:
- Frequency: Minimal (~$0.75/mo) / Standard (~$1.50/mo) / More (~$3/mo) / Max (~$7.50/mo) / Every (~$15/mo)
- Personalization: Anonymous / Stack only / Full — more sharing = more relevant ads (may earn more via better targeting); prompts/code/keys NEVER shared
- Surface: Strip only / Cards+Banners
- Block categories (multi-select): auth / database / payments / infra / monitoring / food / crypto / ai
  Warn: blocking high-CPM categories (food ~$12, crypto) lowers earnings

**Step 3 — Apply changed settings in ONE bash call**
`python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-config frequency <x> && python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-config profile <x>`
If blocked by auto mode, show the command with `!` prefix for user to run directly.

**Step 4 — Confirm**
`python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-config show`

## Arguments
`$ARGUMENTS`: `frequency` | `profile` | `surface` | `block` | `pause` | `resume` → jump to that picker only

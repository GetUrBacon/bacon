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
- Frequency: Minimal (~$0.40/mo) / Standard (~$0.75/mo) / More (~$1.50/mo) / Max (~$3.75/mo) / Every (~$7.50/mo)
- Personalization: Anonymous / Stack only / Full — more sharing = more relevant ads (may earn more via better targeting); prompts/code/keys NEVER shared
- Surfaces (MULTI-SELECT — where ads may appear): In replies / Statusline / Thinking verb. The in-reply format (strip/card/banner) is set by the advertiser, not the user.
- Block categories (multi-select): auth / database / payments / infra / monitoring / food / crypto / ai
  Warn: blocking high-CPM categories (food, crypto) lowers earnings

**Step 3 — Apply changed settings**
bacon-config for frequency/profile/inreply/blocks (ONE bash call):
`python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-config frequency <x> && python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-config profile <x> && python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-config inreply <on|off>`
For the statusline / thinking-verb surfaces (these edit `~/.claude/settings.json` — auto mode may block, offer `!` fallback):
- enable: `bacon-setup statusline-enable --style marquee` / `bacon-setup spinner-enable`
- disable: `bacon-setup statusline-disable` / `bacon-setup spinner-disable`
If blocked by auto mode, show the command with `!` prefix for user to run directly.

**Step 4 — Confirm**
`python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-config show`

## Arguments
`$ARGUMENTS`: `frequency` | `profile` | `inreply` | `surfaces` | `block` | `pause` | `resume` → jump to that picker only

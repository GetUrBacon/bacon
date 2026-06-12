---
description: Configure Bacon ad settings — frequency, profile, surface, blocklist, pause/resume. Use when the user runs /bacon:config or wants to change how ads work.
---

# Bacon Config

CLI at `${CLAUDE_PLUGIN_ROOT}/bin/bacon-config`

## Flow

**Step 1 — Read current settings**
`python3 <path>/bacon-config show`

**Step 2 — Ask (ONE AskUserQuestion call)**
If `$ARGUMENTS` names a specific setting, show only that picker. Otherwise show all 4 at once:
- Frequency: Minimal (~$0.75/mo) / Standard (~$1.50/mo) / More (~$3/mo) / Max (~$7.50/mo) / Every (~$15/mo) — mark current
- Personalization: Anonymous / Stack only / Full (~6.5x CPM) — mark current. Prompts/code/keys NEVER shared.
- Surface: Strip only / Cards+Banners — mark current
- Block categories (multi-select): auth / database / payments / infra / monitoring / food / crypto / ai — warn that blocking high-CPM categories (food $12, crypto) lowers earnings

**Step 3 — Apply in ONE bash call**
Combine only the changed settings:
`python3 <path>/bacon-config frequency <x> && python3 <path>/bacon-config profile <x>`

If blocked by auto mode classifier, show the command prefixed with `!` for the user to run directly.

**Step 4 — Confirm**
`python3 <path>/bacon-config show`

## Commands
```
bacon-config frequency <minimal|standard|more|max|every>
bacon-config profile <anonymous|stack|full>
bacon-config surface <strip|cards>
bacon-config block <category-or-advertiser>
bacon-config unblock <x>
bacon-config pause / resume
```

## Arguments
`$ARGUMENTS`: `frequency` | `profile` | `surface` | `block` | `pause` | `resume` → jump to that picker

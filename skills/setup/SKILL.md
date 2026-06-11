---
description: Set up Bacon — create config, choose ad preferences via interactive form, optionally enable the animated statusline. Use when the user runs /bacon:setup or wants to start earning from ads.
---

# Bacon Setup

First-run onboarding. Gets a developer from "plugin installed" to "earning" using the
same interactive multi-step picker as /bacon:config, plus the consented statusline edit.

CLIs (use `${CLAUDE_PLUGIN_ROOT}/bin/...`, fall back to
`/Users/oscar-rivas/Github/bacon/bin/...` for local testing):
- `bacon-setup`   — config bootstrap, statusline enable/disable, uninstall
- `bacon-config`  — frequency / profile / surface / blocklist writes
- `bacon-earnings` — status readout

## Flow

1. **Already set up?**
   Run `bacon-setup status`. If config exists and is active, show `/bacon:earnings`
   and offer `/bacon:config` to change things — don't re-run onboarding.

2. **Bootstrap config**
   Run `bacon-setup init` (creates ~/.bacon/config.json with defaults).

3. **Preferences — ONE multi-step AskUserQuestion form** (like a plan flow):
   - Q1 Frequency: Minimal / Standard / More / Max / Every (show live $ estimates)
   - Q2 Personalization: Anonymous / Stack only / Full profile
        (state plainly: prompts, code, and keys are NEVER shared)
   - Q3 Surface: Strip only / Cards  (do NOT offer statusline — see note below)
   - Q4 Block categories (multi-select): crypto, food, ai, ... or Nothing
   Apply each answer:
   `bacon-config frequency <x>` · `bacon-config profile <x>` ·
   `bacon-config surface <x>` · `bacon-config block <x>` per blocked item.

   NOTE: The animated statusline tier is built but NOT offered right now — enabling
   it requires editing ~/.claude/settings.json, which skills are blocked from doing.
   Don't present statusline/both. See claudedocs/decision_statusline_deferred.md.

4. **Confirm**
   Run `bacon-config show`. Display the final settings + earnings estimate.
   "✅ Bacon is active. You'll earn on your next prompt. /bacon:earnings to track,
    /bacon:config to adjust, bacon-setup uninstall to remove."

## Uninstall
`bacon-setup uninstall` — restores the original statusline and deactivates ads.
Balance is preserved and still pays out.

## Arguments
`$ARGUMENTS`:
- `statusline` — jump straight to the statusline enable consent + command
- `uninstall` — run uninstall with confirmation

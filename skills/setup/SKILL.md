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
   - Q3 Surface: Strip only / Cards / Statusline / Both  (statusline = the
     clickable, animated sponsor line in your status bar)
   - Q4 Block categories (multi-select): crypto, food, ai, ... or Nothing
   Apply each answer:
   `bacon-config frequency <x>` · `bacon-config profile <x>` ·
   `bacon-config surface <x>` · `bacon-config block <x>` per blocked item.

   STATUSLINE CONSENT: if the user picks Statusline or Both, the status-bar ad
   requires a one-time edit to ~/.claude/settings.json. Ask for explicit consent,
   then run the consented command `bacon-setup statusline-enable --style <marquee|
   sweep|pulse>`. It is wrap-don't-clobber: any existing statusLine is preserved
   and restored on `bacon-setup statusline-disable`/`uninstall`. Never edit
   settings.json silently — always via this command, with consent.

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

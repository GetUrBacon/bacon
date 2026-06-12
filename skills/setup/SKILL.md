---
name: bacon-setup
description: Set up Bacon — create config, choose ad preferences via interactive form, optionally enable the animated statusline. Use when the user runs /bacon:setup or wants to start earning from ads for the first time.
---

# Bacon Setup

CLIs at `${CLAUDE_PLUGIN_ROOT}/bin/`: `bacon-setup` `bacon-config` `bacon-earnings`

## Flow

**Step 1 — Check current state**
`python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-setup status && python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-earnings summary`
- If status shows `Onboarded: ✅ yes` → already configured. Show status + offer `/bacon:config`. Stop here.
- If `Onboarded: ❌ no` (the wizard initialized config but the user hasn't picked preferences yet) → continue to Step 3, skip init.
- If config is missing entirely → run Step 2 first.

**Step 2 — Init (only if config missing)**
`python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-setup init`

**Step 3 — Preferences (ONE AskUserQuestion call, all 4 questions at once)**
- Frequency: Minimal (~$0.40/mo) / Standard (~$0.75/mo) / More (~$1.50/mo) / Max (~$3.75/mo) / Every (~$7.50/mo)
- Personalization: Anonymous / Stack only / Full — more sharing = more relevant ads (may earn more via better targeting); prompts/code/keys NEVER shared
- Surfaces (MULTI-SELECT — where ads may appear): In replies (default) / Statusline / Thinking verb. Note: you don't pick the in-reply format (strip/card/banner) — the advertiser's campaign sets it.
- Block categories (multi-select): crypto / food / ai / payments / infra / or Nothing

**Step 4 — Apply**
Frequency/profile/blocks via bacon-config (ONE bash call):
`python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-config frequency <x> && python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-config profile <x> && python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-config inreply <on|off>`
(`inreply on` if "In replies" was selected, else `off`.)
Then, ONLY for each extra surface the user selected (these edit `~/.claude/settings.json`, so auto mode may block them — offer the `!` fallback):
- Statusline → `python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-setup statusline-enable --style marquee`
- Thinking verb → `python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-setup spinner-enable`

**Step 5 — Confirm & mark complete**
`python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-config show && python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-setup onboarded`
This flips the `onboarded` flag so re-running `/bacon:setup` won't repeat the picker.

## Notes
- Statusline ads require a one-time edit to `~/.claude/settings.json` — only via `bacon-setup statusline-enable`, never directly. Offer it after setup completes with explicit consent.
- `bacon-config` writes to `~/.bacon/config.json`. Auto mode may block it — always have a `!` fallback ready.

## Arguments
- `statusline` → consent prompt + `python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-setup statusline-enable --style marquee`
- `uninstall` → confirm, then `python3 ${CLAUDE_PLUGIN_ROOT}/bin/bacon-setup uninstall`

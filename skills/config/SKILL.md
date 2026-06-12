---
description: Configure Bacon ad settings via interactive menus — frequency, profile/personalization, ad surface, category/advertiser blocklist, pause/resume. Use when the user runs /bacon:config or wants to change how ads work.
---

# Bacon Configuration

Help the user adjust their Bacon ad settings using **interactive AskUserQuestion menus**
(native select / multi-select pickers), then apply each choice with the `bacon-config` CLI.

The CLI lives at `${CLAUDE_PLUGIN_ROOT}/bin/bacon-config`.
Always read current settings first so menus show the active choice:
`python3 <path>/bacon-config show`

## Flow

1. Run `bacon-config show` to read current settings.
2. If the user already named one setting (e.g. "make ads less frequent"), jump
   straight to that single picker.
3. Otherwise present the **full settings form in ONE AskUserQuestion call** with all
   four questions at once (this renders as a multi-step picker, like a plan flow):
   - Q1 Frequency (single-select)
   - Q2 Personalization (single-select)
   - Q3 Surface (single-select)
   - Q4 Block categories (multi-select)
   Mark the user's current value in each so they see what's active.
4. After the form returns, apply each answer with its `bacon-config` command
   (one call per changed setting).
5. Run `bacon-config show` to display the updated state + new earnings estimate.

## Pickers (use AskUserQuestion)

### Frequency (single-select)
Options, each with its live earnings estimate at 500 prompts/day (mark the current one):
- Minimal — 1 per 20 prompts (~$0.75/mo)
- Standard — 1 per 10 prompts (~$1.50/mo)
- More — 1 per 5 prompts (~$3/mo, or ~$9.75 with full profile)
- Max — 1 per 2 prompts (~$7.50/mo, or ~$24 with full profile)
- Every — every prompt (~$15/mo, or ~$49 with full profile)
→ `bacon-config frequency <minimal|standard|more|max|every>`

### Personalization (single-select)
- Anonymous — no data shared, lowest CPM, random ads
- Stack only — languages/deps shared, relevant ads, ~2.5x CPM
- Full — stack + domain shared, most relevant, ~6.5x CPM
Always note: prompts, code, and keys are NEVER shared.
→ `bacon-config profile <anonymous|stack|full>`

### Surface (single-select)
- Strip only — one-line ads in replies (smallest footprint)
- Cards / Banners — boxed ads allowed in replies
→ `bacon-config surface <strip|cards>`
(Note: a statusline ad tier exists in the CLI but is NOT offered — it requires a
manual edit to ~/.claude/settings.json that skills are blocked from making. Do not
present statusline/both as options. See claudedocs/decision_statusline_deferred.md.)

### Block ads (multi-select)
Present categories as a multi-select: auth, database, payments, infra, monitoring,
testing, cicd, email, search, ai, food, crypto. Also allow blocking a named advertiser
(free text). For each selected item run `bacon-config block <item>`.
To unblock, run `bacon-config unblock <item>`.
**Warn the user:** blocking high-value categories (e.g. food/cafe at $12 CPM) can
LOWER their earnings, since it removes top bidders from their auctions.
→ `bacon-config block <category-or-advertiser>` / `bacon-config unblock <x>`

### Pause / Resume
- `bacon-config pause` — ads off, earnings stop
- `bacon-config resume` — back on
Confirm before pausing (earnings stop while paused).

## Notes
- The CLI preserves existing fields (`user_id`, `auction_url`, etc.) — it only edits
  the setting you change. Never hand-write config.json.
- After any change, optionally run `bacon-config show` again to display the full
  updated state with the new earnings estimate.

## Arguments
`$ARGUMENTS` may name a setting to jump straight to its picker:
`frequency` | `profile` | `surface` | `block` | `pause` | `resume`

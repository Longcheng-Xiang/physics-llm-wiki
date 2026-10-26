# Conversation Harvest

Run this after every substantive conversation unless the user explicitly says not to update the vault.

## Step 1 — Classify the conversation output

Choose exactly one primary outcome:

1. `synthesis update` — the useful output is cross-cutting and belongs in an existing synthesis page
2. `source artifact update` — the main durable output is a source-map note, locator, lecture-note summary update, or cleaned source section
3. `workflow/doc update` — the main durable output changes how the vault should be operated
4. `no writeback` — the conversation was ephemeral, speculative, or too low-value to store

## Step 2 — Write back by default

- If the outcome is `synthesis update`, update an existing synthesis page or create one only if it is clearly worth keeping.
- If the outcome is `source artifact update`, update the source map, locator, lecture-note summary, inventory, or cache.
- If the outcome is `workflow/doc update`, update the narrowest appropriate document. Use `CLAUDE.md` only for short, startup-critical, cross-cutting rules; prefer dedicated guides and rules for detail. If detail moves into a narrower guide, add or preserve the loading trigger that ensures the guide is read when relevant.
- If the user says "note that" while correcting agent behavior or workflow interpretation, treat it as a request to make the correction durable for future agents. Update the narrowest relevant rule or document unless the user explicitly says not to edit files.
- If the outcome is `no writeback`, do not force an edit.

## Step 3 — Keep the writeback minimal but real

- Prefer the smallest durable edit that will make the next similar conversation cheaper.
- Prefer the narrowest durable home, not the most visible one.
- If detail is relocated, make the destination readable on demand, not merely discoverable in principle.
- Do not wait for the user to explicitly request a writeback when the information is clearly reusable.
- Do not create decorative pages or duplicative notes merely to satisfy this rule.
- If a live lecture-note PDF read occurred, the default writeback includes an appropriate source-cache update unless extraction quality made that impossible.

## Step 4 — Log it

If any writeback occurred, prepend one line in `log.md` immediately below the comment under `## Entries` so the newest entry is always first:

`YYYY-MM-DD | harvest | brief summary of what was filed back into the vault`

Startup canary: `CANARY_HARVEST_F1`

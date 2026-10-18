---
name: reorder-tunes
description: Reorder the tunes in tunebook.abc by category (barndances, polkas, waltzes, …) per order.txt, moving exactly one tune per git commit. Use when the user types /reorder-tunes [plan|N|all] or asks to sort, reorder, or regroup the tunes in the tunebook.
---

# Reorder tunes

Sort `tunebook.abc` into the category order defined in `order.txt` (next to this file). Within a category, tunes keep their current relative order. The category is taken from each tune's first `R:` line.

**Hard rule: one tune per commit.** Every commit made by this skill moves exactly one tune and changes nothing else — no retagging, no reformatting, no renumbering of `X:`, no PDF.

## Input

- `plan` (or no argument) — show the plan only, change nothing.
- `N` — perform the next N moves, one commit each.
- `all` — perform every remaining move, one commit each.

Default file: `tunebook.abc` in the repo root. Another `.abc` file may be named explicitly.

## Procedure

1. **Plan.** Run `python3 .claude/skills/reorder-tunes/reorder.py plan tunebook.abc` and show the user the category counts, the number of moves, and any unmapped `R:` values.
   - If there are unmapped `R:` values (typos, missing `R:`), point them out. They sort into Other. Fixing a tag is its own separate commit, never bundled with a move — ask the user before doing it.
   - If only planning, stop here.

2. **Preconditions.** Before the first move:
   - `git diff --quiet HEAD -- tunebook.abc` must succeed (no uncommitted edits to the file), and `git diff --cached --quiet` must succeed (nothing else staged). If not, stop and ask the user to commit or stash first. Never fold their pending edits into a move commit.

3. **Move one tune.** Run `python3 .claude/skills/reorder-tunes/reorder.py next tunebook.abc`. It moves exactly one tune (the minimum-move plan: tunes already in a correctly ordered subsequence never move) and prints a `COMMIT:` line.

4. **Verify.** `git diff --stat -- tunebook.abc` must show insertions equal to deletions, and `git status --porcelain` must show no other file changed by the move. If anything else differs, stop and report.

5. **Commit** only that file:
   ```
   git add tunebook.abc
   git commit -m "<text after COMMIT:>" -m "Co-Authored-By: …"   # attribution per the current session reminder
   ```

6. **Repeat** steps 3–5 for the requested number of moves. Report a short summary at the end: moves done, moves remaining.

## Notes

- Blank lines and `%%newpage` directives between tunes stay where they are; only the tune block (from `X:` to the next blank line) moves. Page breaks may therefore land in different places after reordering — mention this, but don't adjust them inside a move commit.
- The PDF becomes stale; don't regenerate it (see CLAUDE.md).
- To change the category order, edit `order.txt` (its own commit), then re-run `plan`.
- Within-category order comes from the commit in `baseline.txt` (tunes matched by `X:` + title), not from current positions — otherwise each move would redefine the order it's meant to preserve. When starting a fresh reordering effort, run `reorder.py init tunebook.abc` and commit the new `baseline.txt` on its own.

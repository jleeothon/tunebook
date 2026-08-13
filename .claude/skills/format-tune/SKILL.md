---
name: format-tune
description: Re-indent the body of a single tune in an .abc tunebook so measures align to a column grid. Use when the user types /format-tune <X|name|"selected lines"> or asks to format a specific tune by its X-number, title, or IDE selection.
---

# Format one tune

Reformat the body of one ABC tune so measures stack vertically per the column-grid rules in CLAUDE.md (sections "Formatting guidelines" and "Lines outside the grid"). CLAUDE.md is in context — refer to it for the alignment rules; don't restate them.

## Input

The argument identifies which tune to format. Accept any of:

- **Tune index** — e.g. `73`, `X:73`, `X: 73`. Locate `X:\s*<N>\b`.
- **`selected lines`** (or `selection`) — use the IDE selection passed in the conversation context (`<ide_selection>` block). The selection's file path tells you which file to edit; the selected lines tell you which tune. If no IDE selection is present, ask.
- **Tune name** — any other free-text argument. Match case-insensitively against `T:` lines across the open/modified `.abc` files (a substring match is fine). If 0 matches, report and ask. If >1 matches, list them with their `X:` numbers and ask which.

Default file when only an X-number is given: `irish tunebook.abc` in the current working directory. If multiple `.abc` files are open or modified, ask which.

## Procedure

1. **Find the tune.**
   - From an X-number: locate `X:\s*<N>\b` in the file.
   - From `selected lines`: take the file from the `<ide_selection>` block and find the `X:` line at or before the selection's first line. The tune still runs from header end to next blank line / next `X:` — don't trust the selection's exact bounds, just use it to pick the tune.
   - From a name: locate the matching `T:` line, then walk back to its `X:` line.

   The body runs from the first line after the header block (X / T / C / R / M / L / K / Q etc.) until the next blank line or next `X:`.

2. **Opt-out check.** If the body contains any of `w:`, `W:`, `V:`, mid-body `K:` or `M:`, or volta brackets (`|1`, `|2`, `:|1`, `:|2`), STOP. Report what was found and ask whether to proceed manually. Do not auto-rewrite — these need human judgment per CLAUDE.md's "Lines outside the grid".

3. **Parse sections.** A section opens at `|:` (or the first body line, which may omit `|:`) and closes at `:|`, `||`, or `|]`. Sections may span multiple lines.

4. **Reflow each section.**
   - Detect anacrusis (pickup) on the first line: any content before the first `|`. Continuation lines need a ghost indent of matching width — spaces only, no `|`.
   - Split each line into measures by `|`. Strip leading/trailing whitespace from each measure's content; preserve the content verbatim.
   - Compute the max content width per column across all lines in the section.
   - Re-emit each line with consistent padding: prefix (`|: `, ghost indent, or empty), then measures joined by ` | ` with each padded to its column width.
   - Place the closing bar per the `|`-anchor rule in CLAUDE.md. Single `|` at the anchor column; `:|` and `||` (with `||` anchored on its second `|`) extend leftward; `|]`, `|:`, and volta digits extend rightward.

5. **Edit** the file via the Edit tool, targeting only the body lines of the tune. Header fields and any comment lines (`%`) must stay untouched.

6. **Report** in the final message that the matching `.pdf` is now stale.

## Invariants

- The notes themselves (every character between bars) must be byte-identical before and after — only inter-character padding changes.
- Header fields and `%` comment lines untouched.
- Within each section, every `|` lands in the same column across all lines.

## What to do if alignment is impossible

If a section has lines with different measure counts (beyond a clean pickup/no-pickup pair) or some other structural irregularity not caught by the opt-out check in step 2, align column-by-column from the left, let the shorter line end where it ends, and note the irregularity in your final message.

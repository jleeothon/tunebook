# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal collection of folk tunebooks written in ABC notation, with rendered PDFs committed alongside the sources. There is no build script, package manifest, or test suite — work is plain text editing of `.abc` files.

## Files

Each `*.abc` is a multi-tune book; the matching `*.pdf` (where present) is its rendered output.

- `tunebook.abc` / `irish tunebook.abc` — Irish trad (barndances, polkas, reels, jigs). `irish tunebook.abc` is the newer, actively edited version; `tunebook.abc` is the older single-book file kept for history. They overlap heavily.
- `czech-slovak tunebook.abc` — Czech/Slovak folk songs with lyrics.
- `scandinavian tunebook.abc` — Scandinavian tunes.
- `kirchen-tunebook.abc` — German hymns, lyrics under `w:` lines.
- `concert-pg-2026.abc` — A small setlist file for a specific concert; not a general tunebook.

## ABC conventions used here

- File-level directives at the top: `%%printtempo false`, `%%infoline true`. Preserve them on new files.
- Tunes are separated by blank lines and begin with `X:` (index). Header order is `X T [C] R M L K` followed by the body.
- Chord symbols are inline quoted strings, e.g. `"G"G4`, `"D7"dedc`, `"C/E"e2dc`.
- Lyrics use `w:` for syllable-aligned lines under the staff and `W:` for free-form additional verses.
- The `Q:` field is repurposed in `czech-slovak tunebook.abc` / `scandinavian tunebook.abc` as a region tag (e.g. `Q: Slovakia`), not a tempo. Leave that convention alone.
- When adding a tune, copy the header style and spacing from neighbouring tunes in the same file rather than imposing a different layout.

## Working directories

The repo lives in iCloud and is reachable at two equivalent paths on this machine:

- `~/Library/Mobile Documents/com~apple~CloudDocs/Scores/Folk Tunebook` (canonical)
- `~/iCloud/scores/Folk Tunebook`

Edits via either path land in the same iCloud-synced files — don't treat them as separate copies. Expect `.DS_Store` noise; do not commit it.

## PDFs

The `*.pdf` files are rendered outputs and are checked in. They are produced externally (e.g. `abcm2ps` then `ps2pdf`, or an editor like EasyABC) — there is no script in the repo to regenerate them. After editing an `.abc`, the matching `.pdf` is stale until rebuilt; do not attempt to regenerate it unless explicitly asked.

## Formatting guidelines

The body of a tune is laid out as a grid: each line is a row of measures, and corresponding measures across lines stack vertically. Preserve this when editing.

- **Section delimiters.** `|:` opens a section, `:|` / `||` / `|]` closes one. The first section may omit `|:`. A section can span multiple lines.
- **Measure separator.** `|` ends each measure. Pad with at least one space on either side (`G2 | dc d2`, not `G2|dcd2`).
- **Vertical alignment.** Across the lines of a section, the `|` ending measure 1 should sit in the same column on every line; the `|` ending measure 2 likewise; and so on. When you change a measure, re-pad the surrounding spaces so the column grid still holds.
- **Bars anchor on `|`.** Every bar marker (`|`, `:|`, `|:`, `|]`, `||`, `|1`, `|2`, `:|1`, `:|2`, `[|`, `.|`, etc.) aligns by its `|` character. Extra characters extend outward into the surrounding spaces: `:` left in `:|`, `]` right in `|]`, both in `:|2`, `:` right in `|:`, the volta digit right in `|2`. For `||`, anchor the second `|`; the first sits one column to its left (so `||` lines up with `:|` — both have an extra character one column left of the anchor). Bars without a `|` character (e.g. `::` for back-to-back repeat) have no anchor; leave them as the author wrote them.
- **Anacrusis (pickup).** A line may start with a partial measure before the first `|`. If the following line has no pickup, indent it with spaces equal to the width of the pickup plus its bar — a "ghost" measure with **no** `|` — so the line's first full measure aligns under the previous line's first full measure.
- **Multi-voice (`V:A`, `V:B`, …).** Treat `V:X ` (directive plus its trailing space) as part of the line prefix, like `|:` or a ghost indent. All voices within a section share one measure grid. See `irish tunebook.abc` X:59 ("The Castle").

Example, from `irish tunebook.abc` ("The Cotillion"):

```
D2    | "G"G4 "D" d4      | "Em"B2AB "G/D" G2AB  | "C"c2B2 A2G2    | "D"FGEF D3 D    |
        "C"E4"D"F4        | "G"GFGA "Em"G2c2     | "C"B2AG "D"A2GF | "G" G6         :|
```

Line 1 has a `D2` pickup; line 2 begins with spaces (no `|`) so `"C"E4"D"F4` lands under `"G"G4 "D" d4`. Line 2 closes with `:|`; its `|` sits in the same column as line 1's `|`, with `:` extending one column to the left.

### Lines outside the grid

Some lines opt out of the measure grid. Leave them untouched, and exclude them when computing column widths for surrounding music lines.

- **Lyric lines (`w:` / `W:`).** Aligned syllable-to-note, not column-to-column. Rewriting them would scramble the lyrics. Common throughout `kirchen-tunebook.abc` and parts of `czech-slovak tunebook.abc`.
- **Mid-body `K:` or `M:` directives.** Hard reset of the grid: the music above and below forms separate sections, indented independently (e.g. `kirchen-tunebook.abc:23` switches key mid-tune). Don't try to align measures across the divider.
- **Comments (`%` at line start).** Outside the grid.
- **Voltas (`|1 … :|2 … ||`).** Voltas usually fit on one line and the two endings have different content lengths — don't force them into a shared column grid with the lines above. The bars themselves still follow the standard anchor rule.
- **Variable measures per line.** If lines within a section have different measure counts beyond a clean pickup/no-pickup pair, align column-by-column from the left and let the shorter line end where it ends. If the structure is too irregular, leave the tune as-is.

### Bulk indenting

When re-indenting many tunes at once, skip any tune that contains `V:`, `w:`/`W:`, mid-body `K:`/`M:`, or volta brackets (`|1`, `|2`, `:|1`, `:|2`). Report which tunes were skipped rather than silently mangling them. In practice this means bulk mode is mainly useful on `irish tunebook.abc`; `kirchen-tunebook.abc` (every tune has lyrics) and `czech-slovak tunebook.abc` (frequent mid-body `K:`/`M:` and voltas) will skip most or all tunes.

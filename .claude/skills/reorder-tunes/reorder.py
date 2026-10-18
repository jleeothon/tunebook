#!/usr/bin/env python3
"""Reorder tunes in an ABC tunebook by category, one tune per invocation.

    reorder.py plan FILE   show category counts and the moves still needed
    reorder.py next FILE   perform exactly one move, print a commit message

A tune is the X: line through the last line before the next blank line.
Everything between tunes (blank lines, %%newpage, comments) stays where it is.
The moves are the minimum needed: tunes on a longest already-ordered
subsequence never move, every other tune moves exactly once.
"""
import re
import sys
from pathlib import Path

ORDER_FILE = Path(__file__).with_name("order.txt")


def load_order():
    cats, by_r, other = [], {}, None
    for line in ORDER_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, _, values = line.partition(":")
        rank = len(cats)
        cats.append(name.strip())
        for v in values.split(","):
            v = v.strip().lower()
            if v == "*":
                other = rank
            elif v:
                by_r[v] = rank
    if other is None:
        sys.exit("order.txt needs an 'Other: *' line")
    return cats, by_r, other


def parse(lines):
    """Return list of tunes as dicts with start/end (end exclusive) line indices."""
    tunes, i = [], 0
    while i < len(lines):
        if re.match(r"X:", lines[i]):
            j = i
            while j < len(lines) and lines[j].strip():
                j += 1
            block = lines[i:j]
            title = next((l[2:].strip() for l in block if l.startswith("T:")), "?")
            r = next((l[2:].strip() for l in block if l.startswith("R:")), "")
            x = lines[i][2:].strip()
            tunes.append(dict(start=i, end=j, title=title, r=r, x=x))
            i = j
        else:
            i += 1
    return tunes


def classify(tunes, by_r, other):
    unknown = []
    for t in tunes:
        key = t["r"].lower()
        t["rank"] = by_r.get(key, other)
        if key not in by_r:
            unknown.append(t)
    return unknown


def lis_keep(seq):
    """Indices (into seq) of one longest strictly increasing subsequence."""
    tails, tails_idx, prev = [], [], [-1] * len(seq)
    import bisect
    for i, v in enumerate(seq):
        k = bisect.bisect_left(tails, v)
        if k == len(tails):
            tails.append(v)
            tails_idx.append(i)
        else:
            tails[k] = v
            tails_idx[k] = i
        prev[i] = tails_idx[k - 1] if k else -1
    keep, i = set(), tails_idx[-1] if tails_idx else -1
    while i != -1:
        keep.add(i)
        i = prev[i]
    return keep


def analyse(path):
    cats, by_r, other = load_order()
    lines = path.read_text().split("\n")
    tunes = parse(lines)
    unknown = classify(tunes, by_r, other)
    target = sorted(range(len(tunes)), key=lambda i: (tunes[i]["rank"], i))
    pos_in_target = {cur: k for k, cur in enumerate(target)}
    seq = [pos_in_target[i] for i in range(len(tunes))]
    keep = lis_keep(seq)
    moves = [cur for cur in target if cur not in keep]
    return cats, lines, tunes, unknown, target, keep, moves


def label(t):
    return f"X:{t['x']} \"{t['title']}\" (R: {t['r'] or '—'})"


def cmd_plan(path):
    cats, _, tunes, unknown, _, _, moves = analyse(path)
    counts = [0] * len(cats)
    for t in tunes:
        counts[t["rank"]] += 1
    for name, n in zip(cats, counts):
        print(f"{n:4d}  {name}")
    print(f"\n{len(tunes)} tunes, {len(moves)} move(s) needed.")
    if unknown:
        print("\nUnmapped R: values (sorted into Other):")
        for t in unknown:
            print("  " + label(t))
    if moves:
        print("\nMoves, in order:")
        for cur in moves:
            t = tunes[cur]
            print(f"  {label(t)} -> {cats[t['rank']]}")


def cmd_next(path):
    cats, lines, tunes, _, target, keep, moves = analyse(path)
    if not moves:
        print("Already in order; nothing to move.")
        return
    cur = moves[0]
    t = tunes[cur]
    k = target.index(cur)
    anchor = tunes[target[k - 1]] if k else None  # predecessor in target order

    block = lines[t["start"]:t["end"]]
    gap_end = t["end"]
    while gap_end < len(lines) and not lines[gap_end].strip():
        gap_end += 1
    blanks = max(1, gap_end - t["end"])

    # Remove the tune and the blank lines directly after it.
    rest = lines[:t["start"]] + lines[gap_end:]
    shift = lambda i: i - (gap_end - t["start"]) if i >= gap_end else i

    if anchor is None:
        first = min(shift(u["start"]) for u in tunes if u is not t)
        new = rest[:first] + block + [""] * blanks + rest[first:]
        where = "to the top"
    else:
        at = shift(anchor["end"])
        new = rest[:at] + [""] * blanks + block + rest[at:]
        where = f"after X:{anchor['x']} \"{anchor['title']}\""

    path.write_text("\n".join(new))
    cat = cats[t["rank"]]
    print(f"Moved {label(t)} {where}.")
    print(f"{len(moves) - 1} move(s) remaining.")
    print(f"COMMIT: Move {t['title']} to {cat.lower()}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("plan", "next"):
        sys.exit(__doc__)
    {"plan": cmd_plan, "next": cmd_next}[sys.argv[1]](Path(sys.argv[2]))

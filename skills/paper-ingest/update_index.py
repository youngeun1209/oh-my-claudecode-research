#!/usr/bin/env python3
"""Idempotent upsert into the reading-library record index (index.csv).

Keyed by `bibkey`: running twice with the same bibkey updates the existing row in
place (no duplicate). Only fields passed on the command line are changed; omitted
fields keep their current value (or the empty placeholder on first insert).

The CSV path is required (--csv) — it lives inside the project's paper library dir
(## Research stack `Paper library dir`, default docs/papers/), which is project-specific,
so this script hardcodes nothing.

Usage:
  update_index.py --csv <library>/bibliographic-management/index.csv \
      --bibkey smith2022 \
      --year 2022 --first_author "Smith A" \
      --title "Graph attention for ..." \
      --venue "Proc XYZ 2022" --doi 10.xxxx/xxxxx \
      --bucket core-method --status read --relevance "intro;R3" \
      --in_project no --pdf refs/smith-2022.pdf \
      --figure figs/smith2022-fig4.png --added_on 2026-06-29
"""
import argparse
import csv
import os
import sys

COLUMNS = [
    "bibkey", "year", "first_author", "title", "venue", "doi",
    "bucket", "status", "relevance", "in_project", "pdf", "figure", "added_on",
]
PLACEHOLDER = "—"


def load_rows(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_rows(path, rows):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    # Stable sort: by year then bibkey, so the file stays human-scannable.
    def key(r):
        y = r.get("year", "")
        return (y if y not in ("", PLACEHOLDER) else "9999", r.get("bibkey", ""))
    rows = sorted(rows, key=key)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, PLACEHOLDER) or PLACEHOLDER for c in COLUMNS})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", required=True,
                    help="path to the library's bibliographic-management/index.csv")
    ap.add_argument("--bibkey", required=True)
    for col in COLUMNS:
        if col == "bibkey":
            continue
        ap.add_argument("--" + col, default=None)
    args = ap.parse_args()

    rows = load_rows(args.csv)
    by_key = {r["bibkey"]: r for r in rows if r.get("bibkey")}

    row = by_key.get(args.bibkey)
    action = "updated"
    if row is None:
        row = {c: PLACEHOLDER for c in COLUMNS}
        row["bibkey"] = args.bibkey
        rows.append(row)
        action = "inserted"

    # Apply only the fields explicitly provided on the CLI.
    for col in COLUMNS:
        if col == "bibkey":
            continue
        val = getattr(args, col)
        if val is not None:
            row[col] = val

    write_rows(args.csv, rows)
    print(f"index.csv: {action} '{args.bibkey}' ({len(rows)} rows total)")


if __name__ == "__main__":
    sys.exit(main())

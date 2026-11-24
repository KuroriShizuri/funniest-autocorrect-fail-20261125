#!/usr/bin/env python3
"""Be There Spoon — Funniest Autocorrect Fail (make.fun).

Writes one 138-character autocorrect-fail line to entry.txt.
Stdlib only. No trailing newline: the file holds exactly the line.
"""

import argparse
import os
import sys
import tempfile

LINE = (
    "I texted my boss \u2018running late, be there soon\u2019 \u2014 "
    "autocorrect sent \u2018running late, be there spoon\u2019, "
    "and now the whole office calls me Spoon."
)


def validate(line: str) -> None:
    """The gate: 1-199 characters, UTF-8 text, not only whitespace."""
    if not 1 <= len(line) <= 199:
        raise ValueError(f"line is {len(line)} chars, must be 1-199")
    if not line.strip():
        raise ValueError("line is only whitespace")
    line.encode("utf-8")


def write_entry(out_dir: str) -> str:
    validate(LINE)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(LINE)
    with open(path, "rb") as f:
        data = f.read()
    if data != LINE.encode("utf-8"):
        raise ValueError("entry.txt is not byte-identical to the line")
    # Re-validate the file on disk itself (non-empty, 1-199 chars) so a
    # bad artifact fails the run instead of shipping silently.
    try:
        written = data.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("entry.txt is not valid UTF-8")
    validate(written)
    return path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="validate only, write nothing")
    parser.add_argument("--self-test", action="store_true",
                        help="validate + byte-identical write/read "
                             "round-trip in a temp dir")
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except ValueError as exc:
        print(f"invalid entry: {exc}", file=sys.stderr)
        return 1


def _run(args) -> int:
    if args.check:
        validate(LINE)
        print(f"OK: {len(LINE)} chars, gate 1-199")
        return 0
    if args.self_test:
        validate(LINE)
        with tempfile.TemporaryDirectory() as tmp:
            path = write_entry(tmp)
            print(f"OK: self-test wrote {path} "
                  f"({len(LINE)} chars, byte-identical)")
        return 0
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    path = write_entry(out_dir)
    print(f"wrote {path} ({len(LINE)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

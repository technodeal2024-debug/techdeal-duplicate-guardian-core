"""Read-only sample: python examples/basic_usage.py /path/to/test-folder"""
from __future__ import annotations
import argparse
from pathlib import Path
from techdeal_duplicate_guardian_core import scan_duplicates

def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only duplicate discovery")
    parser.add_argument("directory", type=Path)
    args = parser.parse_args(argv)
    result = scan_duplicates(args.directory)
    print(f"Files scanned: {result.scanned_files}; groups: {len(result.groups)}; skipped: {len(result.skipped)}")
    for group in result.groups:
        print(f"SHA-256={group.digest} size={group.size}, matching paths={len(group.paths)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

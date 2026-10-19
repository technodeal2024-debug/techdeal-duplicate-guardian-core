"""Small CLI with safe, non-mutating output."""
import argparse
import json
import sys
from .scanner import scan_duplicates

def main(argv=None):
    p = argparse.ArgumentParser(description="Find duplicate files (READ ONLY; never deletes files)")
    p.add_argument("directory", help="Directory to scan")
    p.add_argument("--max-files", type=int, default=100_000)
    p.add_argument("--json", action="store_true", help="Print report as JSON; may reveal local paths")
    args = p.parse_args(argv)
    try:
        report = scan_duplicates(args.directory, max_files=args.max_files)
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"Scan failed: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report.as_dict(), indent=2))
    else:
        print(f"Scanned {report.scanned_files} files; {len(report.groups)} duplicate groups; {len(report.skipped)} skipped")
        for index, group in enumerate(report.groups, 1):
            print(f"\nGroup {index}: {group.size} bytes, SHA256={group.digest}")
            for name in group.paths:
                print(f"  {name}")
        if report.skipped:
            print(f"\nSkipped {len(report.skipped)} entries; --json shows details", file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())

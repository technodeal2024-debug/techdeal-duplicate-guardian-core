# TechDeal Duplicate Guardian Core

[![CI](https://img.shields.io/badge/tests-pytest-blue)](#development)

An independently implemented, **read-only**, local duplicate-file discovery library and CLI. Built for open-source collaboration; **not a source release of the commercial TechDeal Duplicate Guardian Android/Windows apps**.

## Safety first
- Scans local directories without network requests, telemetry, deletion or modification.
- Size pre-filter → first-block SHA-256 → streaming full-file SHA-256.
- Skips file/directory symlinks and avoids treating hardlinks to the same inode as distinct copies.
- Detects common file changes during hashing and reports unreadable/changed files as skipped.
- **No automatic cleanup.** Hash matches are evidence for review, not permission to delete.
- This is **not adversarial-race-proof**: a hostile actor controlling parent directories can replace paths while scanning. Avoid hostile or concurrently mutated directories.

## Install (Python 3.10+)
```sh
python -m pip install .
td-duplicates /path/to/folder
# JSON contains local filenames: do not publish personal scan reports
td-duplicates /path/to/folder --json
```
On Windows:
```powershell
py -m pip install .
td-duplicates "C:\\Users\\YourName\\Documents"
```

## Python API
```python
from techdeal_duplicate_guardian_core import scan_duplicates
report = scan_duplicates("/path/to/folder")
for group in report.groups:
    print(group.size, group.digest, group.paths)
```

## Limitations
- Not a similarity finder (image perceptual hashes or fuzzy matches).
- Local filesystem paths only; Android scoped storage/SAF URIs are **not** directly supported.
- No Windows app/Android APK included; no guarantee of compatibility with proprietary apps.
- Read-only means no file-content writes by this library; files may be accessed/atime changed by OS filesystem policy.
- Large trees may require time; default maximum is 100,000 discovered files.
- Python package and CLI only in v0.1.0. The cross-platform/Android SDK is a future roadmap item, not currently implemented.

## Development
```sh
python -m pip install -e '.[test]'
python -m pytest -q
```
See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and [docs/PUBLISHING.md](docs/PUBLISHING.md).

## License and trademark
Code: MIT License, subject to a rights-holder authorization check before first public publication. TechDeal AI names and trademarks are not granted by the code license.

**Independent OSS project, not an OpenAI-endorsed project.** Open-sourcing a project does not guarantee eligibility for any Codex/OpenAI grant.
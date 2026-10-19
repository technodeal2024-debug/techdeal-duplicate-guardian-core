# TechDeal Duplicate Guardian Core

[![CI](https://github.com/technodeal2024-debug/techdeal-duplicate-guardian-core/actions/workflows/tests.yml/badge.svg)](https://github.com/technodeal2024-debug/techdeal-duplicate-guardian-core/actions/workflows/tests.yml)

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

## Safe demonstration
Run the included example against a small test folder that you own:
    python examples/basic_usage.py /path/to/test-folder
The example is read-only. Do not publish unredacted scan reports: output can reveal local file paths.

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

## Public project status
- This repository is public and newly established; no community adoption is claimed yet.
- No tagged release or PyPI distribution is claimed. Check the GitHub Releases page for updates.
- Please report genuine bugs or contribute reproducible tests. See CHANGELOG.md, docs/ROADMAP.md, and MAINTAINERS.md.

## Development
```sh
python -m pip install -e '.[test]'
python -m pytest -q
```
See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and [docs/PUBLISHING.md](docs/PUBLISHING.md).

## License and trademark
Code is distributed under the MIT License in LICENSE. The code license does not grant rights to TechDeal AI trademarks or any private commercial product.

**Independent OSS project, not an OpenAI-endorsed project.** Open-sourcing a project does not guarantee eligibility for any Codex/OpenAI grant.
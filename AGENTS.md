# OSS coding-assistant guidance

Before editing, read README.md, SECURITY.md, docs/ARCHITECTURE.md and CONTRIBUTING.md.
- Keep the core local, offline and read-only; never add file deletion, moves, uploads or telemetry without explicit project scope review.
- Do not import proprietary commercial app source, keys or client data.
- Include real regression tests and run python -m pytest -q; confirm cross-platform CI after changes.
- Preserve explicit privacy and filesystem-race limitations.
- Never fabricate users, releases, GitHub stars or grant eligibility.
- Human maintainer approval is required for public release tags and version changes.

# Architecture and threat model

1. Enumerate local regular files without following directory symlinks.
2. Group candidates by size and skip redundant hardlink identities.
3. Hash a bounded prefix with SHA-256 to narrow likely matches.
4. Stream full-file SHA-256 and verify path/file metadata around reads.
5. Return groups and skipped-path diagnostics; never delete or modify scanned files.

## Limitations
- Parent-directory swaps by malicious actors are not fully prevented; avoid untrusted directories.
- On-disk files can change concurrently; best-effort change checks are not forensic integrity guarantees.
- Some filesystems can update access timestamps on read.
- JSON reports include local paths and should not be shared publicly without redaction.
- No Android scoped storage, cloud sync, fuzzy matching or deletion support.
- No performance claims are made without published and reproducible measurements.

"""Read-only, conservative duplicate scanner. Never changes user files."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict
import hashlib
import os
import stat

CHUNK_SIZE = 1024 * 1024

@dataclass(frozen=True)
class DuplicateGroup:
    size: int
    digest: str
    paths: tuple[str, ...]

@dataclass(frozen=True)
class ScanReport:
    groups: tuple[DuplicateGroup, ...]
    scanned_files: int
    candidate_files: int
    skipped: tuple[str, ...]
    def as_dict(self) -> dict:
        return {"groups": [{"size": g.size, "sha256": g.digest, "paths": list(g.paths)} for g in self.groups],
                "scanned_files": self.scanned_files, "candidate_files": self.candidate_files,
                "skipped": list(self.skipped)}

def _identity(path: Path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
        raise ValueError("not a regular non-symlink file")
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)

def _read_digest(path: Path, expected, max_bytes: int | None = None) -> str:
    if _identity(path) != expected:
        raise ValueError("file changed before reading")
    # O_NOFOLLOW blocks final-component symlink swaps on POSIX, when supported.
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns) != expected:
            raise ValueError("file changed during opening")
        h = hashlib.sha256()
        remaining = max_bytes
        while True:
            n = CHUNK_SIZE if remaining is None else min(CHUNK_SIZE, remaining)
            if n <= 0:
                break
            block = os.read(fd, n)
            if not block:
                break
            h.update(block)
            if remaining is not None:
                remaining -= len(block)
        after = os.fstat(fd)
        if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) != expected:
            raise ValueError("file changed during reading")
    finally:
        os.close(fd)
    if _identity(path) != expected:
        raise ValueError("file changed after reading")
    return h.hexdigest()

def _stable_digest(path: Path, expected: tuple, max_bytes: int | None = None) -> tuple[str, tuple]:
    """Retry once when a file's timestamps settle without changing size/inode.

    Never accept a replaced file or a size change. Every successful hash still
    performs the strict before/open/after metadata checks in _read_digest.
    """
    try:
        return _read_digest(path, expected, max_bytes), expected
    except ValueError as exc:
        if not str(exc).startswith("file changed"):
            raise
        refreshed = _identity(path)
        if refreshed[:3] != expected[:3]:
            raise
        return _read_digest(path, refreshed, max_bytes), refreshed


def scan_duplicates(root: str | Path, *, max_files: int = 100_000, sample_bytes: int = 65536) -> ScanReport:
    """Discover exact duplicate candidates via size, sampled SHA-256 and full SHA-256.

    Never deletes, moves, links, or edits files. Directory symlinks are not followed.
    Paths are local; no networking. Concurrently modified files are excluded.
    Filesystem traversal can't guarantee protection from adversarial parent-dir swaps.
    """
    root = Path(root).absolute()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("root must be a real existing directory (not symlink)")
    if max_files < 1 or not (0 < sample_bytes <= 1024 * 1024):
        raise ValueError("invalid file limit or sample size")
    by_size: dict[int, list[tuple[Path, tuple]]] = defaultdict(list)
    skipped: list[str] = []
    seen_inodes: set[tuple[int, int]] = set()
    scanned = 0
    def onerror(error):
        skipped.append(f"directory error: {error}")
    for base, dirs, files in os.walk(root, topdown=True, followlinks=False, onerror=onerror):
        dirs[:] = sorted(d for d in dirs if not (Path(base) / d).is_symlink())
        for filename in sorted(files):
            path = Path(base) / filename
            try:
                info = _identity(path)
                # Multiple hardlinks to the same inode are one physical file.
                inode = (info[0], info[1])
                if inode in seen_inodes:
                    continue
                if scanned >= max_files:
                    raise RuntimeError(f"scan limit reached ({max_files} files); choose a smaller folder")
                seen_inodes.add(inode)
                scanned += 1
                by_size[info[2]].append((path, info))
            except RuntimeError:
                raise
            except (OSError, ValueError) as exc:
                skipped.append(f"{path}: {exc}")
    candidate_files = sum(len(v) for v in by_size.values() if len(v) > 1)
    results: list[DuplicateGroup] = []
    for size, entries in sorted(by_size.items()):
        if len(entries) < 2:
            continue
        by_sample = defaultdict(list)
        for path, expected in entries:
            try:
                digest, stable_info = _stable_digest(path, expected, sample_bytes)
                by_sample[digest].append((path, stable_info))
            except (OSError, ValueError) as exc:
                skipped.append(f"{path}: {exc}")
        for sampled in by_sample.values():
            if len(sampled) < 2:
                continue
            by_full = defaultdict(list)
            for path, expected in sampled:
                try:
                    digest, stable_info = _stable_digest(path, expected)
                    by_full[digest].append((path, stable_info))
                except (OSError, ValueError) as exc:
                    skipped.append(f"{path}: {exc}")
            for digest, matching in by_full.items():
                stable = []
                for path, expected in matching:
                    try:
                        if _identity(path) == expected:
                            stable.append(str(path))
                        else:
                            skipped.append(f"{path}: changed since hashing")
                    except (OSError, ValueError) as exc:
                        skipped.append(f"{path}: {exc}")
                if len(stable) >= 2:
                    results.append(DuplicateGroup(size=size, digest=digest, paths=tuple(sorted(stable))))
    results.sort(key=lambda g: (-g.size, g.paths))
    return ScanReport(tuple(results), scanned, candidate_files, tuple(skipped))

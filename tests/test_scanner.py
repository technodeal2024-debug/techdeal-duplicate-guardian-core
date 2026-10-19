import json
import os
import pytest
from techdeal_duplicate_guardian_core import scan_duplicates
from techdeal_duplicate_guardian_core.cli import main

def test_exact_duplicates_and_near_duplicates(tmp_path):
    for name, data in {'a.txt': b'alpha', 'b.txt': b'alpha', 'c.txt': b'alphb', 'd.txt': b'other'}.items():
        (tmp_path / name).write_bytes(data)
    report = scan_duplicates(tmp_path)
    assert len(report.groups) == 1
    assert [os.path.basename(p) for p in report.groups[0].paths] == ['a.txt', 'b.txt']
    assert (tmp_path / 'a.txt').read_bytes() == b'alpha'

def test_empty_files(tmp_path):
    (tmp_path/'a').touch(); (tmp_path/'b').touch()
    assert len(scan_duplicates(tmp_path).groups) == 1

def test_symlinks_ignored(tmp_path):
    (tmp_path/'actual').mkdir(); (tmp_path/'actual'/'a').write_text('x')
    (tmp_path/'actual'/'b').write_text('x')
    try:
        (tmp_path/'link').symlink_to(tmp_path/'actual', target_is_directory=True)
        (tmp_path/'actual'/'alias').symlink_to(tmp_path/'actual'/'a')
    except (OSError, NotImplementedError):
        pytest.skip('Symlink creation unavailable')
    report = scan_duplicates(tmp_path)
    assert len(report.groups) == 1 and len(report.groups[0].paths) == 2
    with pytest.raises(ValueError): scan_duplicates(tmp_path/'link')

def test_hardlinks_same_inode_not_duplicate(tmp_path):
    (tmp_path/'a').write_bytes(b'hello')
    try: os.link(tmp_path/'a', tmp_path/'b')
    except OSError: pytest.skip('Hardlinks unavailable')
    assert scan_duplicates(tmp_path).groups == ()

def test_file_limit(tmp_path):
    for n in range(3): (tmp_path/str(n)).write_text(str(n))
    with pytest.raises(RuntimeError): scan_duplicates(tmp_path, max_files=2)

def test_json_cli(tmp_path, capsys):
    (tmp_path/'a').write_text('x'); (tmp_path/'b').write_text('x')
    assert main([str(tmp_path),'--json']) == 0
    data=json.loads(capsys.readouterr().out)
    assert data['scanned_files'] == 2 and len(data['groups']) == 1

def test_invalid_root(tmp_path):
    with pytest.raises(ValueError): scan_duplicates(tmp_path/'missing')

def test_distinct_full_hash(tmp_path):
    prefix=b'x'*70000
    (tmp_path/'a').write_bytes(prefix+b'a'); (tmp_path/'b').write_bytes(prefix+b'b')
    assert scan_duplicates(tmp_path).groups == ()


def test_metadata_timestamp_settling_retries_once(tmp_path, monkeypatch):
    """Transient mtime shift with unchanged size/inode can be safely rehashed."""
    from techdeal_duplicate_guardian_core import scanner
    (tmp_path / 'a').write_bytes(b'repeated')
    (tmp_path / 'b').write_bytes(b'repeated')
    original = scanner._read_digest
    triggered = []

    def metadata_shift(path, expected, max_bytes=None):
        if path.name == 'b' and max_bytes is not None and not triggered:
            triggered.append(True)
            st = path.stat()
            os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000_000))
        return original(path, expected, max_bytes)

    monkeypatch.setattr(scanner, '_read_digest', metadata_shift)
    result = scan_duplicates(tmp_path)
    assert len(result.groups) == 1
    assert result.skipped == ()


def test_changed_size_is_not_retried_as_duplicate(tmp_path, monkeypatch):
    """Substantial mutation/replacement remains excluded from duplicate reports."""
    from techdeal_duplicate_guardian_core import scanner
    (tmp_path / 'a').write_bytes(b'same')
    (tmp_path / 'b').write_bytes(b'same')
    original = scanner._read_digest
    triggered = []

    def mutate(path, expected, max_bytes=None):
        if path.name == 'b' and max_bytes is not None and not triggered:
            triggered.append(True)
            path.write_bytes(b'changed-to-a-longer-file')
        return original(path, expected, max_bytes)

    monkeypatch.setattr(scanner, '_read_digest', mutate)
    result = scan_duplicates(tmp_path)
    assert result.groups == ()
    assert any('b:' in name or 'b\\:' in name or 'b: file changed' in name for name in result.skipped)

"""Validate the published read-only usage example."""
import runpy
from pathlib import Path

def test_readonly_example_reports_group(tmp_path, capsys):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_bytes(b"same-demo-data")
    b.write_bytes(b"same-demo-data")
    script = Path(__file__).resolve().parents[1] / "examples" / "basic_usage.py"
    main = runpy.run_path(str(script))["main"]
    before = (a.read_bytes(), b.read_bytes())
    assert main([str(tmp_path)]) == 0
    assert "groups: 1" in capsys.readouterr().out
    assert (a.read_bytes(), b.read_bytes()) == before

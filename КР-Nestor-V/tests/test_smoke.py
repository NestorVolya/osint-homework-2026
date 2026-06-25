"""
Smoke tests — no API keys required.
Run: pytest tests/test_smoke.py
"""

import sys
from pathlib import Path
import tempfile
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.gates.input_gate import validate_seed, detect_seed_type
from pipeline.gates.safety_gate import strip_html, sanitize_for_llm
from pipeline.storage.db import Database
from pipeline.storage.archive import create_run_dir, zip_run


# --- input_gate ---

def test_validate_seed_valid():
    assert validate_seed("some_handle", "nickname") == "some_handle"

def test_validate_seed_email():
    assert validate_seed("user@example.com", "email") == "user@example.com"

def test_validate_seed_empty():
    with pytest.raises(ValueError, match="empty"):
        validate_seed("", "nickname")

def test_validate_seed_banned():
    with pytest.raises(ValueError, match="placeholder"):
        validate_seed("test", "nickname")

def test_validate_seed_nickname_with_space():
    with pytest.raises(ValueError, match="spaces"):
        validate_seed("first last", "nickname")

def test_detect_seed_type_email():
    assert detect_seed_type("user@mail.com") == "email"

def test_detect_seed_type_fullname():
    assert detect_seed_type("Іван Франко") == "fullname"

def test_detect_seed_type_nickname():
    assert detect_seed_type("coolhandle") == "nickname"


# --- safety_gate ---

def test_strip_html_removes_scripts():
    html = "<p>Hello</p><script>alert(1)</script><style>body{}</style>"
    result = strip_html(html)
    assert "Hello" in result
    assert "<script>" not in result
    assert "alert" not in result

def test_sanitize_truncates():
    text = "a" * 10000
    result = sanitize_for_llm(text, max_chars=100)
    assert len(result) <= 100


# --- db ---

def test_db_init_creates_tables():
    with tempfile.TemporaryDirectory() as tmp:
        db = Database(Path(tmp) / "test.sqlite")
        tables = db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        names = {r[0] for r in tables}
        assert "sources" in names
        assert "events" in names
        assert "statements" in names
        assert "links" in names
        assert "accounts" in names
        assert "geoclusters" in names
        assert "locations" in names
        db.close()

def test_db_insert_source():
    with tempfile.TemporaryDirectory() as tmp:
        db = Database(Path(tmp) / "test.sqlite")
        db.insert_source("src1", "actor1", "https://example.com", "Title", "text body")
        sources = db.get_sources("actor1")
        assert len(sources) == 1
        assert sources[0]["url"] == "https://example.com"
        db.close()


# --- archive ---

def test_create_run_dir():
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = create_run_dir(Path(tmp))
        assert run_dir.exists()
        assert (run_dir / "raw").exists()
        assert (run_dir / "artifacts").exists()
        assert (run_dir / "report").exists()

def test_zip_run():
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = create_run_dir(Path(tmp))
        (run_dir / "raw" / "test.json").write_text("{}", encoding="utf-8")
        zip_path = zip_run(run_dir)
        assert zip_path.exists()
        assert zip_path.suffix == ".zip"


# --- dry-run integration ---

def test_dry_run_end_to_end():
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pipeline.run",
         "--seed", "Олексій Чекаль",
         "--seed_type", "fullname",
         "--dry-run"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0, result.stderr

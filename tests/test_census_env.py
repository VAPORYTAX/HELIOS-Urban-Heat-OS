from pathlib import Path
from app.realdata.census import _read_env_file

def test_env_parser(tmp_path: Path):
    p = tmp_path / ".env"
    p.write_text("CENSUS_API_KEY=abc123\n", encoding="utf-8")
    assert _read_env_file(p)["CENSUS_API_KEY"] == "abc123"

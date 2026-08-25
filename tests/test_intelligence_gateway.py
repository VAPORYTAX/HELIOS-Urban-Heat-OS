from app.intelligence.gateway import _extract_json

def test_extract_json_plain():
    assert _extract_json('{"a":1}') == {"a":1}

def test_extract_json_fenced():
    assert _extract_json('```json\n{"a":1}\n```') == {"a":1}

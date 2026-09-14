from utils.json_parser import extract_json


def test_extracts_json_array_from_fence():
    raw = '```json\n[{"index": 0, "text": "هوك"}]\n```'
    assert extract_json(raw)[0]["text"] == "هوك"


def test_extracts_json_object_from_surrounding_text():
    raw = 'نتيجة التحليل:\n{"ok": true, "score": 8}\nانتهى.'
    data = extract_json(raw)
    assert data["ok"] is True
    assert data["score"] == 8

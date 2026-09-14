from utils.validation import validate_script

def test_empty_script():
    ok, _ = validate_script("")
    assert not ok

def test_short_script():
    ok, _ = validate_script("hello")
    assert not ok

def test_valid_script():
    ok, _ = validate_script("ا" * 400)
    assert ok

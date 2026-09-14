from config.constants import MAX_SCRIPT_CHARS

def validate_script(script: str):
    if not script or not script.strip(): return False, "اكتب السكريبت الأول."
    if len(script.strip()) < 300: return False, "السكريبت قصير جدًا. الصق نصًا فيه مادة كافية لبناء هوك حقيقي."
    if len(script) > MAX_SCRIPT_CHARS: return False, "السكريبت أطول من الحد المسموح."
    return True, "OK"

def safe_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:] if lines else lines
        if lines and lines[-1].strip().startswith("```"): lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()

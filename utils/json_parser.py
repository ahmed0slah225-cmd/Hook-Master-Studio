import json
import re


def extract_json(text: str):
    """Tolerant parser for model responses that contain fenced or mixed JSON."""
    if not text:
        raise ValueError("Empty model response")
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.I).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        starts = [i for i, c in enumerate(cleaned) if c in "[{]"]
        for start in starts:
            for end in range(len(cleaned), start + 1, -1):
                try:
                    return json.loads(cleaned[start:end])
                except json.JSONDecodeError:
                    continue
    raise ValueError("Could not extract valid JSON from model response")

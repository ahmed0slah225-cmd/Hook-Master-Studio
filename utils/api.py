import json, re, time
from google import genai
from config.settings import AppSettings

class GeminiService:
    def __init__(self, settings: AppSettings):
        self.settings = settings
        if not settings.api_key: raise RuntimeError("GEMINI_API_KEY غير موجود. ضعه في Streamlit Secrets أو في الحقل الجانبي.")
        self.client = genai.Client(api_key=settings.api_key)

    def generate(self, prompt: str, temperature: float = 0.8):
        response = self.client.models.generate_content(model=self.settings.model, contents=prompt)
        return getattr(response, "text", "") or ""

    def generate_json(self, prompt: str):
        raw = self.generate(prompt)
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.I|re.M)
        try: return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, flags=re.S)
            if match: return json.loads(match.group(0))
            raise

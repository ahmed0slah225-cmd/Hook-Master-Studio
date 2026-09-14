from google import genai

from config.settings import AppSettings
from utils.json_parser import extract_json


class GeminiService:
    def __init__(self, settings: AppSettings):
        self.settings = settings
        if not settings.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY غير موجود. ضعه في Streamlit Secrets أو في الحقل الجانبي."
            )
        self.client = genai.Client(api_key=settings.api_key)

    def generate(self, prompt: str, temperature: float = 0.8):
        response = self.client.models.generate_content(
            model=self.settings.model,
            contents=prompt,
        )
        return getattr(response, "text", "") or ""

    def generate_json(self, prompt: str):
        raw = self.generate(prompt)
        return extract_json(raw)

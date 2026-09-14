from __future__ import annotations

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
        try:
            response = self.client.models.generate_content(
                model=self.settings.model,
                contents=prompt,
            )
        except Exception as exc:
            # Preserve the original provider error so the pipeline can distinguish
            # transient failures such as 429/503 from permanent configuration errors.
            message = str(exc).strip() or exc.__class__.__name__
            model = self.settings.model
            if "404" in message or "not found" in message.lower():
                raise RuntimeError(
                    f"Gemini model غير متاح: {model}. تأكد من اسم الموديل في Streamlit Secrets "
                    f"(GEMINI_MODEL). الخطأ الأصلي: {message}"
                ) from exc
            if "401" in message or "403" in message or "api key" in message.lower():
                raise RuntimeError(
                    f"مشكلة في Gemini API Key أو صلاحيات المفتاح. الخطأ الأصلي: {message}"
                ) from exc
            if "429" in message or "resource_exhausted" in message.lower():
                raise RuntimeError(
                    f"Gemini رفض الطلب مؤقتًا بسبب الـquota/rate limit. سيتم إعادة المحاولة تلقائيًا. "
                    f"الخطأ الأصلي: {message}"
                ) from exc
            raise RuntimeError(f"Gemini API error: {message}") from exc

        text = getattr(response, "text", "") or ""
        if not text.strip():
            raise RuntimeError(
                f"Gemini رجّع استجابة فارغة باستخدام الموديل {self.settings.model}."
            )
        return text

    def generate_json(self, prompt: str):
        raw = self.generate(prompt)
        try:
            return extract_json(raw)
        except Exception as exc:
            preview = raw[:500].replace("\n", " ")
            raise RuntimeError(
                f"Gemini رجّع نصًا لكن لم أستطع تحويله إلى JSON. بداية الاستجابة: {preview}"
            ) from exc

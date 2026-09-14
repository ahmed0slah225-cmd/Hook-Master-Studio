import os
from dataclasses import dataclass
import streamlit as st
from .constants import DEFAULT_MODEL, DEFAULT_RETRY_SECONDS, MAX_RETRIES


@dataclass
class AppSettings:
    api_key: str = ""
    model: str = DEFAULT_MODEL
    retry_seconds: int = DEFAULT_RETRY_SECONDS
    max_retries: int = MAX_RETRIES

    @classmethod
    def from_streamlit(cls):
        secrets_key = ""
        secrets_model = ""
        try:
            secrets_key = st.secrets.get("GEMINI_API_KEY", "")
            secrets_model = st.secrets.get("GEMINI_MODEL", "")
        except Exception:
            pass

        api_key = secrets_key or os.getenv("GEMINI_API_KEY", "")
        model = secrets_model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL) or DEFAULT_MODEL
        return cls(api_key=api_key, model=model.strip())

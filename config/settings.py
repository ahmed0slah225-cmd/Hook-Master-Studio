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
        try: secrets_key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception: pass
        return cls(api_key=secrets_key or os.getenv("GEMINI_API_KEY", ""), model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL))

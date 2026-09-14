from dataclasses import dataclass
import streamlit as st
from config.settings import AppSettings

@dataclass
class UIConfig:
    audience: str
    duration: int
    style: str

def render_sidebar(settings: AppSettings):
    with st.sidebar:
        st.header("⚙️ التحكم")
        key = st.text_input("Gemini API Key", value="", type="password", help="يمكنك بدلًا من ذلك وضعه في Streamlit Secrets.")
        if key: settings.api_key = key
        settings.model = st.text_input("Model", value=settings.model)
        style = st.selectbox("أسلوب الكتابة", ["مصري طبيعي", "دحيح/تفسيري", "قصصي سينمائي", "اقتصادي قريب من الناس", "تحفيزي واقعي"])
        audience = st.text_input("الجمهور الافتراضي", "شباب وبنات يحبوا الحكي والأمثلة")
        duration = st.slider("مدة الفيديو", 1, 180, 15)
        st.caption("يتم تحليل السكريبت أولًا ثم توليد عدة زوايا وتقييمها قبل اختيار الفائز.")
    return UIConfig(audience, duration, style)

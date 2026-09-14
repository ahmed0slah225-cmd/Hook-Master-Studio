import streamlit as st

from config.settings import AppSettings
from core.pipeline import HookPipeline
from utils.validation import validate_script
from ui.sidebar import render_sidebar
from ui.results import render_results

st.set_page_config(
    page_title="Hook Master Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

settings = AppSettings.from_streamlit()
config = render_sidebar(settings)

st.title("🎯 Hook Master Studio")
st.caption("حوّل السكريبت الجاهز إلى هوك مبني على أقوى نقطة في المحتوى، مش مجرد جملة مثيرة.")

script = st.text_area("الصق السكريبت هنا", height=420, placeholder="الصق السكريبت الكامل هنا...")
col1, col2 = st.columns([3, 1])
with col1:
    audience = st.text_input("الجمهور المستهدف", value=config.audience)
with col2:
    duration = st.number_input("مدة الفيديو بالدقائق", min_value=1, max_value=180, value=config.duration)

if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "pipeline_state" not in st.session_state:
    st.session_state.pipeline_state = None
if "last_error" not in st.session_state:
    st.session_state.last_error = None

run = st.button("🚀 حلّل السكريبت وابنِ الهوك", type="primary", use_container_width=True)
retry = st.button("🔄 إعادة المحاولة من آخر مرحلة", use_container_width=True)


def show_pipeline_error(exc: Exception, retry_available: bool = True):
    message = str(exc).strip() or exc.__class__.__name__
    if "quota" in message.lower() or "429" in message.lower() or "rate limit" in message.lower():
        st.error("⚠️ Gemini وصل لحد الاستخدام المؤقت (Quota/Rate Limit). النظام حاول تلقائيًا؛ لو استمر، انتظر قليلًا ثم استخدم إعادة المحاولة.")
    elif "API Key" in message or "api key" in message.lower():
        st.error("🔑 مفتاح Gemini فيه مشكلة أو غير موجود. راجع GEMINI_API_KEY في Streamlit Secrets أو المفتاح الموجود في الشريط الجانبي.")
    elif "model غير متاح" in message or "not found" in message.lower():
        st.error("🤖 اسم موديل Gemini غير متاح لهذا المفتاح. راجع GEMINI_MODEL في Secrets.")
    elif "JSON" in message:
        st.error("🧩 Gemini رجّع استجابة غير صالحة للنظام. الحالة محفوظة، ويمكن إعادة المحاولة.")
    else:
        st.error("حصل خطأ أثناء تنفيذ المرحلة الحالية. الحالة محفوظة ويمكنك إعادة المحاولة.")

    with st.expander("🔍 تفاصيل الخطأ التقني", expanded=True):
        st.code(message)


if run:
    ok, message = validate_script(script)
    if not ok:
        st.error(message)
    else:
        pipeline = HookPipeline(settings)
        with st.status("جاري بناء الهوك مرحلة بمرحلة...", expanded=True) as status:
            try:
                result = pipeline.run(script=script, audience=audience, duration=duration, style=config.style)
                st.session_state.last_result = result
                st.session_state.pipeline_state = pipeline.state
                st.session_state.last_error = None
                status.update(label="تم الانتهاء", state="complete")
            except Exception as exc:
                st.session_state.pipeline_state = pipeline.state
                st.session_state.last_error = str(exc)
                status.update(label="توقف التنفيذ — الحالة محفوظة", state="error")
                show_pipeline_error(exc)

if retry and st.session_state.pipeline_state:
    pipeline = HookPipeline(settings)
    with st.status("بنرجع من آخر مرحلة محفوظة...", expanded=True) as status:
        try:
            result = pipeline.resume(st.session_state.pipeline_state)
            st.session_state.last_result = result
            st.session_state.pipeline_state = pipeline.state
            st.session_state.last_error = None
            status.update(label="اكتملت إعادة المحاولة", state="complete")
        except Exception as exc:
            st.session_state.pipeline_state = pipeline.state
            st.session_state.last_error = str(exc)
            status.update(label="لسه فيه مشكلة — الحالة محفوظة", state="error")
            show_pipeline_error(exc)

if st.session_state.last_error:
    with st.expander("📌 آخر خطأ محفوظ"):
        st.code(st.session_state.last_error)

if st.session_state.last_result:
    render_results(st.session_state.last_result)

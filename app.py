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
                # The pipeline keeps its last completed checkpoint, so retry can continue.
                st.session_state.pipeline_state = pipeline.state
                st.session_state.last_error = str(exc)
                status.update(label="حصل عطل مؤقت — الحالة محفوظة", state="error")
                st.error("العملية وقفت عند آخر مرحلة مكتملة. اضغط إعادة المحاولة، وهتكمل من الحالة المحفوظة.")

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
            status.update(label="لسه فيه مشكلة مؤقتة", state="error")
            st.warning("لسه المشكلة موجودة. الحالة محفوظة؛ جرّب زر إعادة المحاولة مرة تانية.")

if st.session_state.last_error:
    with st.expander("تفاصيل آخر خطأ"):
        st.code(st.session_state.last_error)

if st.session_state.last_result:
    render_results(st.session_state.last_result)

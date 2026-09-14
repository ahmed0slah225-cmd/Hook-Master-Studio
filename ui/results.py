import streamlit as st

def render_results(result):
    st.divider(); st.subheader("🏆 الهوك المختار")
    if result.winner:
        st.success(result.winner.text)
        st.write(f"**النوع:** {result.winner.hook_type}")
        if result.winner.score:
            st.metric("النتيجة", f"{result.winner.score.total:.1f}/10")
            cols = st.columns(4)
            for i,(k,v) in enumerate(result.winner.score.dimensions.items()):
                cols[i%4].metric(k, f"{v}/10")
        st.info(result.explanation)
    st.subheader("🧪 كل المرشحين")
    for i,c in enumerate(result.candidates, 1):
        with st.expander(f"{i}. {c.hook_type} — {c.score.total if c.score else 0:.1f}/10"):
            st.write(c.text); st.caption(c.rationale)
            if c.score:
                st.write("نقاط القوة:", " • ".join(c.score.strengths) or "—")
                st.write("نقاط الضعف:", " • ".join(c.score.weaknesses) or "—")
    with st.expander("🔍 تحليل السكريبت"):
        st.json(result.analysis.model_dump())

import streamlit as st


def render_results(result):
    st.divider()
    st.subheader("🏆 الهوك الفائز")

    if result.winner:
        st.success(result.winner.text)
        st.write(f"**النوع:** {result.winner.hook_type}")
        st.caption(f"جولات التحسين: {result.winner.iteration}")

        if result.winner.score:
            st.metric("النتيجة النهائية", f"{result.winner.score.total:.1f}/10")
            cols = st.columns(4)
            for i, (key, value) in enumerate(result.winner.score.dimensions.items()):
                cols[i % 4].metric(key, f"{value:.1f}/10")
            if result.winner.score.strengths:
                st.write("**ليه قوي؟**", " • ".join(result.winner.score.strengths))
            if result.winner.score.weaknesses:
                st.write("**إيه اللي كان ممكن يضعفه؟**", " • ".join(result.winner.score.weaknesses))

        st.info(result.explanation)

    st.subheader("🧪 كل المرشحين")
    for i, candidate in enumerate(result.candidates, 1):
        score = candidate.score.total if candidate.score else 0
        with st.expander(f"{i}. {candidate.hook_type} — {score:.1f}/10"):
            st.write(candidate.text)
            if candidate.rationale:
                st.caption(candidate.rationale)
            if candidate.retention_notes:
                st.write("**ملاحظات الاحتفاظ:**")
                for note in candidate.retention_notes[-4:]:
                    st.caption(note)
            if candidate.score:
                st.write("**نقاط القوة:**", " • ".join(candidate.score.strengths) or "—")
                st.write("**نقاط الضعف:**", " • ".join(candidate.score.weaknesses) or "—")
                if candidate.score.risk_flags:
                    st.warning("مخاطر: " + " • ".join(candidate.score.risk_flags))

    report = result.quality_report or {}
    with st.expander("🧠 تقرير غرفة الكتابة والجودة"):
        st.json(report)

    with st.expander("🔍 تحليل السكريبت"):
        st.json(result.analysis.model_dump())

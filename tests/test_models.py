from config.models import HookCandidate, HookScore, PipelineState

def test_pipeline_state_roundtrip():
    state = PipelineState(script="abc", audience="شباب", duration=20, style="مصري", stage=2)
    restored = PipelineState.model_validate(state.model_dump())
    assert restored.script == "abc"
    assert restored.stage == 2

def test_hook_score_accepts_risk_flags():
    score = HookScore(total=82, risk_flags=["minor_genericity"])
    hook = HookCandidate(text="ليه بنعمل كده؟", hook_type="curiosity", score=score)
    assert hook.score.total == 82

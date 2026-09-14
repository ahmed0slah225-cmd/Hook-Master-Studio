from core.quality_gate import QualityGate
from config.models import HookCandidate, ScriptAnalysis

def test_rejects_empty_hook():
    result = QualityGate().evaluate(HookCandidate(text="", hook_type="curiosity"), ScriptAnalysis())
    assert not result["passed"]
    assert "empty" in result["flags"]

def test_rejects_meta_cta():
    result = QualityGate().evaluate(HookCandidate(text="اشترك في القناة قبل ما نبدأ لأن ده مهم", hook_type="story"), ScriptAnalysis())
    assert not result["passed"]
    assert "meta_or_cta" in result["flags"]

from core.quality_gate import QualityGate
from config.models import HookCandidate, ScriptAnalysis


def test_rejects_empty_hook():
    result = QualityGate().evaluate(HookCandidate(text="", hook_type="curiosity"), ScriptAnalysis())
    assert not result["passed"]
    assert "empty" in result["flags"]


def test_rejects_meta_cta():
    result = QualityGate().evaluate(
        HookCandidate(text="اشترك في القناة قبل ما نبدأ لأن ده مهم", hook_type="story"),
        ScriptAnalysis(),
    )
    assert not result["passed"]
    assert "meta_or_cta" in result["flags"]


def test_rejects_scene_only_opener():
    result = QualityGate().evaluate(
        HookCandidate(
            text="تخيل إنك الساعة 1 بالليل قاعد قدام اللاب توب ومش عارف تركز في شغلك.",
            hook_type="story",
        ),
        ScriptAnalysis(),
    )
    assert not result["passed"]
    assert "scene_setting_without_immediate_hook" in result["flags"]


def test_rejects_generic_opener_without_payload():
    result = QualityGate().evaluate(
        HookCandidate(
            text="خليني أقولك حاجة مهمة جدًا عن النجاح وتغيير حياتك بشكل كامل من النهارده.",
            hook_type="story",
        ),
        ScriptAnalysis(),
    )
    assert not result["passed"]
    assert "generic_opener" in result["flags"]

from config.models import ScriptAnalysis
from core.agent_orchestrator import AgentOrchestrator


class FakeAI:
    def generate_json(self, prompt):
        if 'أعد JSON array فقط، وكل عنصر' in prompt:
            return [
                {"hook_type": "curiosity", "text": "ليه بتكرر نفس الغلط كل يوم؟", "rationale": "question"},
                {"hook_type": "story", "text": "كل يوم كان بيبدأ بنفس الطريقة، لحد ما لاحظ حاجة غريبة.", "rationale": "story"},
            ]
        if 'لجنة نقد' in prompt:
            return [
                {"index": 0, "approved": True, "issues": [], "rewrite_direction": ""},
                {"index": 1, "approved": False, "issues": ["generic"], "rewrite_direction": "اجعل البداية أكثر تحديداً"},
            ]
        if 'أعد كتابة الهوكات' in prompt:
            return [{"index": 1, "text": "كل يوم كان بيبدأ بنفس الغلطة الصغيرة، ومحدش كان واخد باله ليه بتتكرر."}]
        return []


def test_batched_generation_returns_hook_candidates():
    orchestrator = AgentOrchestrator(FakeAI())
    candidates = orchestrator.generate_candidates(ScriptAnalysis(), "script", "شباب", "مصري")
    assert len(candidates) == 2
    assert candidates[0].hook_type == "curiosity"


def test_batched_rewrite_updates_only_flagged_candidate():
    orchestrator = AgentOrchestrator(FakeAI())
    candidates = orchestrator.generate_candidates(ScriptAnalysis(), "script", "شباب", "مصري")
    reviews = orchestrator.critique_candidates(candidates, "script", ScriptAnalysis())
    updated = orchestrator.rewrite_candidates(candidates, reviews, ScriptAnalysis(), "شباب")
    assert updated[0].text == candidates[0].text
    assert updated[1].iteration == 1

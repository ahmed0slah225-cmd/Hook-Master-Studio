from __future__ import annotations

from typing import Any

from agents.critic_agent import CriticAgent
from agents.humanizer_agent import HumanizerAgent
from agents.hook_agent import HookAgent


class AgentOrchestrator:
    """Coordinates specialized agents without letting one prompt do everything."""

    HOOK_TYPES = (
        "curiosity", "story", "shocking", "emotional",
        "problem-driven", "contradiction", "open-loop", "pattern-interrupt"
    )

    def __init__(self, ai):
        self.ai = ai
        self.hook_agent = HookAgent(ai)
        self.critic = CriticAgent(ai)
        self.humanizer = HumanizerAgent(ai)

    def generate_candidates(self, analysis, script: str, audience: str, style: str):
        candidates = []
        for hook_type in self.HOOK_TYPES:
            raw = self.hook_agent.ask(
                self._writer_prompt(analysis, script, audience, style, hook_type)
            )
            text = self._extract_text(raw)
            if text:
                candidates.append({"text": text, "hook_type": hook_type, "iteration": 0})
        return candidates

    def critique(self, hook: str, script: str) -> dict[str, Any]:
        review = self.critic.review(hook, script)
        return {"review": review}

    def humanize(self, hook: str) -> str:
        return self._extract_text(self.humanizer.rewrite(hook))

    def rewrite_from_critique(self, hook: str, critique: str, analysis, audience: str) -> str:
        prompt = f"""
أنت كاتب هوكات يوتيوب مصري محترف.
أعد كتابة الهوك فقط بناءً على النقد التالي.
لا تغيّر الفكرة الأساسية ولا تخترع معلومة غير موجودة في التحليل.
خليه طبيعي، قابل للنطق، محدد، ويفتح فجوة فضول حقيقية.
ممنوع: التحية، مقدمة عامة، طلب اشتراك، مبالغة رخيصة، كشف الإجابة.

الجمهور: {audience}
الهوك الحالي:
{hook}

النقد:
{critique}

التحليل:
{analysis.model_dump_json()}

أخرج الهوك النهائي فقط بدون علامات اقتباس أو شرح.
"""
        return self._extract_text(self.ai.generate(prompt))

    def _writer_prompt(self, analysis, script, audience, style, hook_type):
        return f"""
أنت عضو في غرفة كتابة هوكات يوتيوب، ولست كاتب محتوى عام.
اكتب هوكًا من نوع: {hook_type}.
اللغة: مصرية طبيعية، قابلة للكلام بصوت بشري.
الجمهور: {audience}
ستايل القناة: {style}

مهم جدًا:
- ابدأ من مشكلة أو لحظة أو تناقض حقيقي موجود داخل السكريبت.
- لا تبدأ بتحية أو شرح موضوع الفيديو.
- لا تستخدم كليشيهات مثل: في الفيديو ده، خليني أقولك، النهاردة هنعرف.
- لا تخترع رقمًا أو دراسة أو قصة غير موجودة.
- لا تكشف الإجابة كاملة.
- اجعل المشاهد يشعر أن هناك شيئًا محددًا يجب أن يعرفه إذا أكمل.
- الهوك ليس عنوانًا ولا ملخصًا؛ هو بداية قصة/سؤال.

تحليل السكريبت:
{analysis.model_dump_json()}

السكريبت:
{script}

أخرج الهوك فقط.
"""

    @staticmethod
    def _extract_text(value: Any) -> str:
        text = str(value or "").strip()
        if text.startswith("```"):
            text = text.strip("`").replace("json\n", "", 1).strip()
        return text.strip('"').strip()

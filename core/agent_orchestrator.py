from __future__ import annotations

from typing import Any

from agents.humanizer_agent import HumanizerAgent
from config.models import HookCandidate


class AgentOrchestrator:
    """Coordinates the hook-writing team while minimizing unnecessary API calls."""

    HOOK_TYPES = (
        "curiosity", "story", "shocking", "emotional",
        "problem-driven", "contradiction", "open-loop", "pattern-interrupt"
    )

    def __init__(self, ai):
        self.ai = ai
        self.humanizer = HumanizerAgent(ai)

    def generate_candidates(self, analysis, script: str, audience: str, style: str):
        prompt = f"""
أنت غرفة كتابة Hooks مكوّنة من عدة كتاب محترفين.
اكتب 8 هوكات مختلفة لنفس السكريبت، واحد لكل زاوية:
{', '.join(self.HOOK_TYPES)}

الجمهور: {audience}
ستايل القناة: {style}

قواعد صارمة:
- مصري طبيعي قابل للنطق، مش لغة مقال.
- ابدأ من أقوى مشكلة/لحظة/تناقض موجود فعلاً في السكريبت.
- ممنوع التحية أو شرح موضوع الفيديو في أول جملة.
- ممنوع: "في الفيديو ده"، "خليني أقولك"، "النهاردة هنعرف".
- ممنوع اختراع أرقام أو دراسات أو قصص.
- ممنوع كشف الإجابة كاملة.
- كل هوك لازم يكون له سبب واضح يخلي المشاهد يكمل.
- الهوك بداية قصة أو سؤال، وليس عنواناً أو ملخصاً.

التحليل:
{analysis.model_dump_json()}

السكريبت:
{script}

أعد JSON array فقط، وكل عنصر:
{{"hook_type":"...","text":"...","rationale":"..."}}
"""
        data = self.ai.generate_json(prompt)
        if isinstance(data, dict):
            data = data.get("candidates", data.get("hooks", []))
        if not isinstance(data, list):
            raise ValueError("Hook writer returned an invalid candidate list")
        candidates = []
        for item in data:
            if not isinstance(item, dict):
                continue
            text = self._extract_text(item.get("text"))
            hook_type = str(item.get("hook_type", "")).strip() or "custom"
            if text:
                candidates.append(HookCandidate(
                    text=text,
                    hook_type=hook_type,
                    rationale=str(item.get("rationale", "")),
                    iteration=0,
                ))
        return candidates

    def critique_candidates(self, candidates, script: str, analysis) -> list[dict[str, Any]]:
        payload = [
            {"index": i, "hook_type": c.hook_type, "text": c.text}
            for i, c in enumerate(candidates)
        ]
        prompt = f"""
أنت لجنة نقد لهوكس يوتيوب.
راجع كل الهوكات التالية كمشاهد متشكك.
ابحث عن: العمومية، التصنع، clickbait كاذب، كشف الإجابة، ضعف الفضول، غياب التفاصيل، ضعف الصلة بالسكريبت.
لا تعيد الكتابة الآن.

التحليل:
{analysis.model_dump_json()}

السكريبت:
{script}

الهوكات:
{payload}

أعد JSON array فقط بعنصر لكل هوك:
{{"index":0,"approved":true,"issues":[],"rewrite_direction":"..."}}
"""
        data = self.ai.generate_json(prompt)
        if isinstance(data, dict):
            data = data.get("reviews", data.get("critiques", []))
        return data if isinstance(data, list) else []

    def rewrite_candidates(self, candidates, reviews, analysis, audience: str) -> list[HookCandidate]:
        tasks = []
        for review in reviews:
            if not isinstance(review, dict):
                continue
            if review.get("approved") is True and not review.get("issues"):
                continue
            try:
                index = int(review.get("index"))
                candidate = candidates[index]
            except (ValueError, TypeError, IndexError):
                continue
            tasks.append({
                "index": index,
                "hook_type": candidate.hook_type,
                "current": candidate.text,
                "direction": review.get("rewrite_direction", ""),
                "issues": review.get("issues", []),
            })

        if not tasks:
            return candidates

        prompt = f"""
أنت كبير محرري Hooks باللهجة المصرية.
أعد كتابة الهوكات الموجودة في القائمة فقط.
لا تغيّر الفكرة الأساسية ولا تخترع معلومة.
اجعلها طبيعية، محددة، قابلة للنطق، وتفتح فجوة فضول حقيقية.
ممنوع التحية، CTA، المبالغة الرخيصة، كشف الإجابة، أو لغة AI.

الجمهور: {audience}
التحليل:
{analysis.model_dump_json()}

المهام:
{tasks}

أعد JSON array فقط:
{{"index":0,"text":"النسخة الجديدة"}}
"""
        data = self.ai.generate_json(prompt)
        if isinstance(data, dict):
            data = data.get("rewrites", data.get("candidates", []))
        if not isinstance(data, list):
            return candidates

        for item in data:
            if not isinstance(item, dict):
                continue
            try:
                index = int(item.get("index"))
                new_text = self._extract_text(item.get("text"))
                candidate = candidates[index]
            except (ValueError, TypeError, IndexError):
                continue
            if new_text and new_text != candidate.text:
                candidate.text = new_text
                candidate.iteration += 1
        return candidates

    def humanize(self, hook: str) -> str:
        return self._extract_text(self.humanizer.rewrite(hook))

    @staticmethod
    def _extract_text(value: Any) -> str:
        text = str(value or "").strip()
        if text.startswith("```"):
            text = text.strip("`").replace("json\n", "", 1).strip()
        return text.strip('"').strip()

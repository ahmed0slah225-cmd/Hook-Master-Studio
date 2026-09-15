from __future__ import annotations

import re
from typing import Any

from agents.humanizer_agent import HumanizerAgent
from config.models import HookCandidate
from .hook_truth_engine import HookTruthEngine


class AgentOrchestrator:
    """Coordinates hook generation, critique, and rewrites around a hook-first strategy."""

    HOOK_TYPES = (
        "curiosity", "problem-driven", "contradiction", "emotional",
        "shocking", "open-loop", "story", "pattern-interrupt"
    )

    SCENE_OPENERS = (
        "تخيل انك", "تخيل إنك", "تخيل إن", "انت دلوقتي", "أنت دلوقتي",
        "انت الساعة", "أنت الساعة", "الساعة 1", "الساعة واحدة", "صحيت الصبح",
        "قاعد قدام", "قاعد أمام", "واقف قدام", "واقف أمام", "راجع من الشغل",
        "رجعت من الشغل", "بصيت في المراية", "وانت رايح الشغل", "وأنت رايح الشغل"
    )

    def __init__(self, ai):
        self.ai = ai
        self.humanizer = HumanizerAgent(ai)
        self.truth_engine = HookTruthEngine()

    def generate_candidates(self, analysis, script: str, audience: str, style: str):
        truth = self.truth_engine.extract(analysis)
        prompt = f"""
أنت Head of Hook Strategy لفيديو يوتيوب مصري. مهمتك ليست كتابة مقدمة جميلة؛ مهمتك استخراج سبب حقيقي يجعل مشاهدًا غريبًا يكمل المشاهدة.

هذه هي طبقة HOOK TRUTH التي يجب أن تبني عليها الكتابة:
{truth}

أولوية الهوك:
سبب المشاهدة > وضوح الفكرة > فجوة الفضول > الصدق > اللغة الطبيعية > الزخرفة.

اكتب 8 هوكات مختلفة للزوايا:
{', '.join(self.HOOK_TYPES)}

قواعد إلزامية:
- ابدأ بسبب يستحق المشاهدة: ألم، مفارقة، اكتشاف، مخاطرة، سؤال مهم أو وعد محدد.
- أول جملة يجب أن تقدم Hook payload فوريًا. لا تبدأ بوصف الوقت أو المكان أو الحالة.
- مصري طبيعي جدًا وقابل للنطق بصوت بشري.
- 2 إلى 5 جمل، تقريبًا 18 إلى 55 كلمة.
- ممنوع أن يبدأ أي هوك بـ: "تخيل إنك"، "أنت دلوقتي"، "أنت الساعة"، "الساعة 1 بالليل"، "قاعد قدام اللاب" أو أي مشهد يومي عام مشابه.
- ممنوع افتتاحية سينمائية عامة ثم تأجيل الفكرة الحقيقية.
- القصة أو المشهد مسموح فقط لو كان من أول جملة يحمل صراعًا/مفارقة/اكتشافًا واضحًا مرتبطًا بالسكريبت.
- ممنوع "في الفيديو ده"، "النهاردة هنتكلم"، "خليني أقولك"، "تعالى أقولك"، التحية، CTA، أو العبارات المستهلكة.
- ممنوع اختراع أرقام أو دراسات أو قصص.
- لا تعطِ الإجابة النهائية بالكامل.
- لا تحول الهوك إلى عنوان أو ملخص.
- لو كان النوع Story، ابدأ أيضًا بالخطاف الحقيقي ثم يمكن إدخال لقطة قصصية قصيرة، وليس العكس.
- لو لم توجد زاوية صالحة لنوع معين، ابتكر أقرب زاوية صادقة بدل حشو مشهد.

الجمهور: {audience}
ستايل القناة: {style}
التحليل:
{analysis.model_dump_json()}
السكريبت:
{script}

أعد JSON array فقط:
{{"hook_type":"...","text":"...","rationale":"ما السبب الحقيقي الذي يجعل المشاهد يكمل؟"}}
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
أنت ناقد هوكات يوتيوب شديد القسوة. لا تنبهر بالصياغة الجميلة.
قيّم كل هوك كمشاهد لا يعرف القناة.

اسأل عن كل هوك:
- هل أول جملة فيها سبب حقيقي للمشاهدة أم مجرد scene-setting؟
- هل توجد فائدة/مفارقة/ألم/خطر/اكتشاف واضح؟
- هل الفضول محدد أم غموض فارغ؟
- هل يمكن نسخه على 100 موضوع آخر؟
- هل يبدأ بمشهد يومي مثل "تخيل إنك" أو "أنت الساعة..." بلا قيمة فورية؟
- هل الوعد موجود فعلًا في السكريبت؟
- هل كشف الإجابة مبكرًا؟
- هل اللغة طبيعية عند النطق؟

قاعدة مهمة: مشهد قصصي وحده ليس Hook. يصبح Hook فقط عندما يحمل التوتر أو المفارقة أو الوعد من البداية.

التحليل:
{analysis.model_dump_json()}
السكريبت:
{script}
الهوكات:
{payload}

أعد JSON array فقط:
{{"index":0,"approved":false,"issues":["scene_setting_without_hook"],"rewrite_direction":"ابدأ من أقوى مفارقة/ألم/اكتشاف في السكريبت، ويمكن استخدام المشهد بعد الخطاف"}}
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

المطلوب:
- ابدأ بالسبب الذي يستحق المشاهدة في أول جملة.
- اربط الهوك بأقوى نقطة فعلية في السكريبت.
- افتح فجوة فضول محددة، لا غموضًا فارغًا.
- اجعل أول جملة فيها قيمة أو توتر أو مفارقة فورًا.
- اجعلها طبيعية ومسموعة، لا مقالًا مكتوبًا.
- 2 إلى 5 جمل، 18 إلى 55 كلمة تقريبًا.

ممنوع كافتتاحية:
"تخيل إنك"، "أنت دلوقتي"، "أنت الساعة"، "الساعة 1 بالليل"، "قاعد قدام اللاب"، أو أي مشهد يومي عام لا يحتوي على خطاف حقيقي من أول لحظة.
ممنوع التحية، CTA، "في الفيديو ده"، وشرح الإجابة كاملة.
لا تختلق أي معلومة.

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

    @classmethod
    def looks_like_scene_opener(cls, text: str) -> bool:
        normalized = re.sub(r"[\"'«»]", "", text or "").strip().lower()
        return any(normalized.startswith(x.lower()) for x in cls.SCENE_OPENERS)

    @staticmethod
    def _extract_text(value: Any) -> str:
        if isinstance(value, dict):
            value = value.get("text", value.get("hook", ""))
        text = str(value or "").strip()
        if text.startswith("```"):
            text = text.strip("`").replace("json\n", "", 1).strip()
        return text.strip('"').strip()

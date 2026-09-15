from __future__ import annotations

import re
from typing import Any

from agents.humanizer_agent import HumanizerAgent
from config.models import HookCandidate


class AgentOrchestrator:
    """Coordinates hook generation, critique, and rewrites around a hook-first strategy."""

    HOOK_TYPES = (
        "curiosity", "problem-driven", "contradiction", "emotional",
        "shocking", "open-loop", "story", "pattern-interrupt"
    )

    # These are not automatically forbidden in all contexts, but a hook that starts
    # with them is treated as a scene-setting opener and must contain a strong hook
    # payload immediately or it will be rejected by the quality gate.
    SCENE_OPENERS = (
        "تخيل انك", "تخيل إنك", "تخيل إن", "انت دلوقتي", "أنت دلوقتي",
        "انت الساعة", "أنت الساعة", "الساعة 1", "الساعة واحدة", "صحيت الصبح",
        "قاعد قدام", "قاعد أمام", "واقف قدام", "واقف أمام", "راجع من الشغل",
        "رجعت من الشغل", "بصيت في المراية", "وانت رايح الشغل", "وأنت رايح الشغل"
    )

    def __init__(self, ai):
        self.ai = ai
        self.humanizer = HumanizerAgent(ai)

    def generate_candidates(self, analysis, script: str, audience: str, style: str):
        prompt = f"""
أنت Head of Hook Strategy لفيديو يوتيوب مصري. مهمتك ليست كتابة مقدمة جميلة؛ مهمتك استخراج سبب حقيقي يجعل مشاهدًا غريبًا يكمل المشاهدة.

قبل الكتابة، استنتج من التحليل والسكريبت:
1) أقوى حقيقة أو اكتشاف.
2) أكبر ألم أو خسارة يشعر بها الجمهور.
3) أقوى مفارقة أو شيء يخالف توقع المشاهد.
4) السؤال الذي سيظل مفتوحًا في عقل المشاهد بعد أول 10 ثوانٍ.
5) الوعد الذي يستحق وقت المشاهد.

أولوية الهوك:
سبب المشاهدة > وضوح الفكرة > فجوة الفضول > الصدق > اللغة الطبيعية > الزخرفة.

اكتب 8 هوكات مختلفة للزوايا:
{', '.join(self.HOOK_TYPES)}

قواعد إلزامية:
- مصري طبيعي جدًا وقابل للنطق بصوت بشري.
- الهوك من 2 إلى 5 جمل، تقريبًا 18 إلى 55 كلمة.
- أول جملة يجب أن تحمل مشكلة أو مفارقة أو اكتشافًا أو سؤالًا مهمًا، وليس مجرد وصف للمكان أو الوقت.
- ممنوع أن يبدأ أي هوك بـ: "تخيل إنك"، "أنت دلوقتي"، "أنت الساعة"، "الساعة 1 بالليل"، "قاعد قدام اللاب" أو أي مشهد يومي عام مشابه.
- ممنوع البدء بمشهد سينمائي عام ثم تأجيل الفكرة الحقيقية.
- القصة أو المشهد مسموح فقط إذا كان يحمل التوتر أو المفارقة من أول جملة ويخدم الفكرة المركزية مباشرة.
- ممنوع "في الفيديو ده"، "النهاردة هنتكلم"، "خليني أقولك"، "تعالى أقولك"، التحية، CTA، أو العبارات المستهلكة.
- لا تستخدم أرقامًا أو دراسات أو قصصًا غير موجودة في السكريبت.
- لا تعطِ الإجابة النهائية بالكامل.
- لا تحول الهوك إلى عنوان أو ملخص للسكريبت.
- كل هوك يجب أن يجيب ضمنيًا: لماذا هذا المشاهد تحديدًا يجب أن يكمل الآن؟
- لو لم توجد زاوية صالحة لنوع معين، ابتكر زاوية مختلفة لكن التزم بالمبدأ السابق.

التحليل:
{analysis.model_dump_json()}

السكريبت:
{script}

أعد JSON array فقط:
{{"hook_type":"...","text":"...","rationale":"اذكر سبب قوة الزاوية وليس شرحًا عامًا"}}
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
- هل الهوك يمكن نسخه على 100 موضوع آخر؟
- هل يبدأ بمشهد يومي مثل "تخيل إنك" أو "أنت الساعة..." بلا قيمة فورية؟
- هل يعد بشيء لا يثبته السكريبت؟
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
{{"index":0,"approved":false,"issues":["scene_setting_without_hook"],"rewrite_direction":"ابدأ من أقوى مفارقة/ألم في السكريبت ثم استخدم المشهد لاحقًا إن لزم"}}
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

المطلوب في كل إعادة كتابة:
- ابدأ بالـpayoff الذي يجعل المشاهد يهتم، لا بوصف مشهد.
- استخدم أقوى نقطة فعلية في السكريبت.
- افتح فجوة فضول محددة.
- اجعل أول جملة ذات قيمة أو توتر فوري.
- اجعلها طبيعية ومسموعة، لا مقالًا مكتوبًا.
- 2 إلى 5 جمل، 18 إلى 55 كلمة تقريبًا.

ممنوع تمامًا كافتتاحية:
"تخيل إنك"، "أنت دلوقتي"، "أنت الساعة"، "الساعة 1 بالليل"، "قاعد قدام اللاب"، أو أي مشهد عام لا يحتوي على خطاف حقيقي من أول لحظة.
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

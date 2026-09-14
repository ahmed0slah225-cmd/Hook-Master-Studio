from __future__ import annotations

import re
from config.models import HookCandidate, ScriptAnalysis


class RetentionEngine:
    """Deterministic retention pass: removes generic openings and strengthens open loops.

    The engine is intentionally deterministic for the moment, but accepts an optional
    AI service so it can be upgraded later without breaking the pipeline constructor.
    """

    BANNED_OPENERS = (
        "أهلا بيكم", "اهلا بيكم", "في الفيديو ده", "في فيديو النهاردة",
        "النهاردة هنتكلم", "لو عايز", "لو كنت", "تعالى أقولك", "خليني أقولك"
    )

    def __init__(self, ai=None):
        # Optional dependency keeps RetentionEngine compatible with both the
        # deterministic implementation and future AI-assisted retention passes.
        self.ai = ai

    def refine_candidates(self, candidates, analysis):
        refined = []
        for c in candidates:
            text = self._clean(c.text)
            notes = list(c.retention_notes)
            if any(text.lower().startswith(x.lower()) for x in self.BANNED_OPENERS):
                notes.append("تم رصد افتتاحية عامة تحتاج كسر النمط")
            if not self._has_specificity(text):
                notes.append("الهوك يحتاج تفصيلة ملموسة من مشكلة المشاهد")
            if not self._has_open_loop(text):
                notes.append("لا توجد فجوة فضول واضحة")
            c.text = text
            c.retention_notes = notes
            refined.append(c)
        return refined

    def final_polish(self, winner, analysis):
        text = self._clean(winner.text)
        text = self._remove_meta_language(text)
        winner.text = text.strip()
        winner.humanized = True
        winner.iteration += 1
        return winner

    def _clean(self, text):
        text = re.sub(r'^\s*[\"\'«»]+|[\"\'«»]+\s*$', '', text or '')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _remove_meta_language(self, text):
        patterns = [r'^الهوك[:：]\s*', r'^Hook[:：]\s*', r'^الافتتاحية[:：]\s*']
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.I)
        return text

    def _has_open_loop(self, text):
        markers = ["بس", "المشكلة", "الغريب", "المفاجأة", "اللي محدش", "ليه", "إزاي", "لكن"]
        return any(m in text for m in markers)

    def _has_specificity(self, text):
        return len(text.split()) >= 12 or bool(re.search(r"\d", text))

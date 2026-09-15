from __future__ import annotations

import re
from config.models import HookCandidate, ScriptAnalysis


class QualityGate:
    """Hard gates that keep scene-setting and generic openings out of the winner pool."""

    SCENE_OPENERS = (
        "تخيل انك", "تخيل إنك", "تخيل إن", "انت دلوقتي", "أنت دلوقتي",
        "انت الساعة", "أنت الساعة", "الساعة 1", "الساعة واحدة", "صحيت الصبح",
        "قاعد قدام", "قاعد أمام", "واقف قدام", "واقف أمام", "راجع من الشغل",
        "رجعت من الشغل", "بصيت في المراية", "وانت رايح الشغل", "وأنت رايح الشغل"
    )

    GENERIC_OPENERS = (
        "أهلا بيكم", "اهلا بيكم", "في الفيديو ده", "في فيديو النهاردة",
        "النهاردة هنتكلم", "خليني أقولك", "تعالى أقولك", "النهاردة هنعرف",
        "لو عايز", "لو كنت"
    )

    def evaluate(self, candidate: HookCandidate, analysis: ScriptAnalysis):
        text = candidate.text.strip()
        normalized = re.sub(r"[\"'«»]", "", text).strip().lower()
        words = text.split()
        flags = []

        if not text:
            flags.append("empty")
        if len(words) < 12:
            flags.append("too_short_for_real_hook")
        if len(words) > 90:
            flags.append("too_long")
        if re.search(r"(اشترك|لايك|كومنت|متنساش|أهلا|اهلا بكم)", text, re.I):
            flags.append("meta_or_cta")
        if text.count("!") > 3:
            flags.append("overhyped")
        if any(normalized.startswith(x.lower()) for x in self.GENERIC_OPENERS):
            flags.append("generic_opener")
        if any(normalized.startswith(x.lower()) for x in self.SCENE_OPENERS):
            flags.append("scene_setting_without_immediate_hook")

        hook_signals = (
            "ليه", "إزاي", "ازاي", "المشكلة", "الغريب", "المفاجأة", "الحقيقة",
            "بس", "لكن", "السبب", "أخطر", "أغلب", "مش زي", "مش إن", "كنت فاكر",
            "هنكتشف", "ممكن تخسر", "من غير ما", "من أول"
        )
        if not any(signal in normalized for signal in hook_signals):
            flags.append("weak_hook_payload")

        if candidate.hook_type in {"curiosity", "open-loop", "contradiction"}:
            has_question = "؟" in text or "?" in text or any(
                x in normalized for x in ("ليه", "إزاي", "ازاي", "إيه", "ايه")
            )
            if not has_question:
                flags.append("weak_curiosity_gap")

        return {"passed": not flags, "flags": flags}

    def filter(self, candidates, analysis):
        accepted, rejected = [], []
        for c in candidates:
            result = self.evaluate(c, analysis)
            if result["passed"]:
                accepted.append(c)
            else:
                if c.score:
                    c.score.risk_flags.extend(result["flags"])
                rejected.append(c)
        return accepted, rejected

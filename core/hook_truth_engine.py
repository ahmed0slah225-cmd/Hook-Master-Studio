from __future__ import annotations

from typing import Any, Dict, List

from config.models import ScriptAnalysis


class HookTruthEngine:
    """Extract the raw reason-to-watch before any stylistic hook writing begins."""

    def extract(self, analysis: ScriptAnalysis) -> Dict[str, Any]:
        strongest = self._first(analysis.strongest_moments)
        pain = analysis.core_problem.strip()
        contradiction = self._first(analysis.conflicts) or self._first(analysis.curiosity_gaps)
        emotion = self._first(analysis.emotional_triggers)
        stakes = analysis.stakes.strip()
        promise = analysis.promise.strip()
        hidden = analysis.hidden_question.strip()
        unique = analysis.unique_angle.strip()

        signals: List[str] = []
        for value in (pain, contradiction, promise, stakes, strongest, hidden, unique, emotion):
            if value and value not in signals:
                signals.append(value)

        if contradiction:
            primary_reason = contradiction
            reason_type = "contradiction"
        elif pain:
            primary_reason = pain
            reason_type = "pain"
        elif strongest:
            primary_reason = strongest
            reason_type = "discovery"
        elif promise:
            primary_reason = promise
            reason_type = "promise"
        else:
            primary_reason = unique or hidden or emotion
            reason_type = "curiosity"

        return {
            "primary_reason": primary_reason,
            "reason_type": reason_type,
            "pain": pain,
            "contradiction": contradiction,
            "discovery": strongest,
            "promise": promise,
            "stakes": stakes,
            "hidden_question": hidden,
            "unique_angle": unique,
            "emotional_signal": emotion,
            "signals": signals[:8],
            "scene_opening_warning": "المشهد ليس سببًا للمشاهدة وحده؛ استخدمه فقط بعد وجود خطاف فعلي.",
        }

    @staticmethod
    def _first(values):
        for value in values or []:
            text = str(value).strip()
            if text:
                return text
        return ""

from __future__ import annotations
import re
from config.models import HookCandidate, ScriptAnalysis

class QualityGate:
    """Hard gates that reject weak hooks before they can become winners."""
    def evaluate(self, candidate: HookCandidate, analysis: ScriptAnalysis):
        text = candidate.text.strip()
        flags = []
        if not text:
            flags.append("empty")
        if len(text.split()) < 8:
            flags.append("too_short")
        if len(text.split()) > 90:
            flags.append("too_long")
        if re.search(r"(اشترك|لايك|كومنت|متنساش|أهلا|اهلا بكم)", text, re.I):
            flags.append("meta_or_cta")
        if text.count("!") > 3:
            flags.append("overhyped")
        if text.count("؟") == 0 and candidate.hook_type in {"curiosity", "open-loop", "contradiction"}:
            flags.append("weak_question_gap")
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

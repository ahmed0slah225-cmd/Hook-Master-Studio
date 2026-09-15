from __future__ import annotations

from core.quality_gate import QualityGate


class HookSelector:
    """Select only hooks that survive hard quality gates; never promote a rejected hook."""

    def __init__(self):
        self.gate = QualityGate()

    def select(self, candidates, analysis=None):
        if not candidates:
            return None

        if analysis is not None:
            valid = []
            for candidate in candidates:
                gate = self.gate.evaluate(candidate, analysis)
                if gate["passed"]:
                    valid.append(candidate)
            candidates = valid

        if not candidates:
            return None

        return max(candidates, key=lambda c: c.score.total if c.score else 0)

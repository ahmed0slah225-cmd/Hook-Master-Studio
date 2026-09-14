from __future__ import annotations
from dataclasses import dataclass
from typing import List

@dataclass
class HookExperiment:
    winner_id: str
    runner_up_id: str
    reason: str

class HookABTester:
    """Ranks close candidates and explains the trade-off instead of hiding it."""
    def compare(self, candidates):
        ranked = sorted(candidates, key=lambda x: x.score.total if x.score else 0, reverse=True)
        if len(ranked) < 2:
            return None
        a, b = ranked[0], ranked[1]
        return HookExperiment(
            winner_id=a.text,
            runner_up_id=b.text,
            reason=f"الأول متقدم بفارق {(a.score.total if a.score else 0) - (b.score.total if b.score else 0):.1f} نقطة."
        )

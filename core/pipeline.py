from __future__ import annotations
from typing import Any
from config.models import PipelineState, HookResult
from utils.api import GeminiService
from utils.retry import retry_transient
from .script_analyzer import ScriptAnalyzer
from .hook_engine import HookEngine
from .scoring_engine import ScoringEngine
from .hook_selector import HookSelector
from .retention_engine import RetentionEngine

class HookPipeline:
    """Orchestrates the complete hook-production workflow with checkpoints."""
    def __init__(self, settings):
        self.settings = settings
        self.ai = GeminiService(settings)
        self.analyzer = ScriptAnalyzer(self.ai)
        self.generator = HookEngine(self.ai)
        self.scorer = ScoringEngine(self.ai)
        self.retention = RetentionEngine(self.ai)
        self.selector = HookSelector()
        self.state: PipelineState | None = None

    @retry_transient(max_attempts=4, delay=5)
    def run(self, script: str, audience: str, duration: int, style: str):
        self.state = PipelineState(script=script, audience=audience, duration=duration, style=style, stage=0)
        self._checkpoint(0)
        self.state.analysis = self.analyzer.analyze(script, audience, style)
        self._checkpoint(1)
        self.state.candidates = self.generator.generate(self.state.analysis, script, audience, style)
        self._checkpoint(2)
        self.state.candidates = self.retention.refine_candidates(self.state.candidates, self.state.analysis)
        for candidate in self.state.candidates:
            if candidate.score is None:
                candidate.score = self.scorer.score(candidate, self.state.analysis, audience)
        self._checkpoint(3)
        self.state.winner = self.selector.select(self.state.candidates)
        if self.state.winner:
            self.state.winner = self.retention.final_polish(self.state.winner, self.state.analysis)
        self.state.completed = True
        self.state.stage = 5
        self._checkpoint(5)
        return self._result()

    def resume(self, state: Any):
        self.state = state if isinstance(state, PipelineState) else PipelineState.model_validate(state)
        if self.state.analysis is None:
            self.state.analysis = self.analyzer.analyze(self.state.script, self.state.audience, self.state.style)
            self._checkpoint(1)
        if not self.state.candidates:
            self.state.candidates = self.generator.generate(self.state.analysis, self.state.script, self.state.audience, self.state.style)
            self._checkpoint(2)
        self.state.candidates = self.retention.refine_candidates(self.state.candidates, self.state.analysis)
        for c in self.state.candidates:
            if c.score is None:
                c.score = self.scorer.score(c, self.state.analysis, self.state.audience)
        self._checkpoint(3)
        self.state.winner = self.selector.select(self.state.candidates)
        if self.state.winner:
            self.state.winner = self.retention.final_polish(self.state.winner, self.state.analysis)
        self.state.completed = True
        self.state.stage = 5
        return self._result()

    def _checkpoint(self, stage: int):
        if self.state:
            self.state.stage = stage

    def _result(self):
        assert self.state is not None and self.state.analysis is not None
        return HookResult(
            analysis=self.state.analysis,
            candidates=self.state.candidates,
            winner=self.state.winner,
            explanation=self._explain(self.state.winner, self.state.analysis),
        )

    def _explain(self, winner, analysis):
        if not winner:
            return "لم يتم العثور على هوك مناسب."
        score = winner.score.total if winner.score else 0
        return (
            f"الهوك الفائز مبني على زاوية {winner.hook_type}. "
            f"تم اختياره لأنه يربط بداية الفيديو بأقوى نقطة في السكريبت، "
            f"ويفتح فجوة فضول واضحة بدون كشف الإجابة كاملة. التقييم النهائي: {score:.1f}/100."
        )

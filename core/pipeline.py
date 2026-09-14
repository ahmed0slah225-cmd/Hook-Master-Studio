from __future__ import annotations

import time
from typing import Any, Callable

from config.models import PipelineState, HookResult
from utils.api import GeminiService
from utils.retry import is_transient_error
from .agent_orchestrator import AgentOrchestrator
from .script_analyzer import ScriptAnalyzer
from .scoring_engine import ScoringEngine
from .hook_selector import HookSelector
from .retention_engine import RetentionEngine
from .quality_gate import QualityGate
from .ab_testing import HookABTester


class HookPipeline:
    """Multi-stage hook factory with checkpoints, critic loops and local retries."""

    MAX_CRITIC_ROUNDS = 2
    MAX_ATTEMPTS = 4
    RETRY_DELAY = 5

    def __init__(self, settings):
        self.settings = settings
        self.ai = GeminiService(settings)
        self.analyzer = ScriptAnalyzer(self.ai)
        self.agents = AgentOrchestrator(self.ai)
        self.scorer = ScoringEngine(self.ai)
        self.retention = RetentionEngine(self.ai)
        self.quality_gate = QualityGate()
        self.selector = HookSelector()
        self.ab_tester = HookABTester()
        self.state: PipelineState | None = None

    def run(self, script: str, audience: str, duration: int, style: str):
        self.state = PipelineState(script=script, audience=audience, duration=duration, style=style, stage=0)
        return self._continue_from_checkpoint()

    def resume(self, state: Any):
        self.state = state if isinstance(state, PipelineState) else PipelineState.model_validate(state)
        return self._continue_from_checkpoint()

    def _continue_from_checkpoint(self):
        assert self.state is not None
        if self.state.analysis is None:
            self._run_stage(1, lambda: self.analyzer.analyze(self.state.script, self.state.audience, self.state.style), "analysis")
            self.state.analysis = self.state.checkpoints.pop("_stage_result")

        if not self.state.candidates:
            self._run_stage(
                2,
                lambda: self.agents.generate_candidates(self.state.analysis, self.state.script, self.state.audience, self.state.style),
                "generation",
            )
            self.state.candidates = self.state.checkpoints.pop("_stage_result")

        self.state.candidates = self.retention.refine_candidates(self.state.candidates, self.state.analysis)
        self._critic_loop()

        for candidate in self.state.candidates:
            candidate.score = self._run_stage(
                3,
                lambda c=candidate: self.scorer.score(c, self.state.analysis, self.state.audience),
                f"score_{candidate.hook_type}",
            )
        self._checkpoint(3)

        accepted, rejected = self.quality_gate.filter(self.state.candidates, self.state.analysis)
        pool = accepted or self.state.candidates
        self.state.winner = self.selector.select(pool)
        if self.state.winner:
            self.state.winner = self.retention.final_polish(self.state.winner, self.state.analysis)

        experiment = self.ab_tester.compare(pool)
        self.state.checkpoints["quality_gate"] = {"accepted": len(accepted), "rejected": len(rejected)}
        self.state.checkpoints["ab_test"] = experiment.__dict__ if experiment else None
        self.state.completed = True
        self.state.stage = 5
        self._checkpoint(5)
        return self._result()

    def _run_stage(self, stage: int, operation: Callable[[], Any], label: str):
        assert self.state is not None
        last = None
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            try:
                result = operation()
                self.state.checkpoints[f"{label}_attempts"] = attempt
                self._checkpoint(stage)
                return result
            except Exception as exc:
                last = exc
                self.state.errors.append(f"{label} attempt {attempt}: {exc}")
                self.state.attempts += 1
                if not is_transient_error(exc) or attempt >= self.MAX_ATTEMPTS:
                    raise
                self.state.checkpoints[f"retry_{label}"] = {
                    "attempt": attempt,
                    "next_retry_seconds": self.RETRY_DELAY,
                    "reason": str(exc),
                }
                time.sleep(self.RETRY_DELAY)
        raise last

    def _critic_loop(self):
        assert self.state is not None and self.state.analysis is not None
        for round_no in range(1, self.MAX_CRITIC_ROUNDS + 1):
            changed = False
            for candidate in self.state.candidates:
                gate = self.quality_gate.evaluate(candidate, self.state.analysis)
                critique = self._run_stage(
                    3,
                    lambda c=candidate: self.agents.critique(c.text, self.state.script),
                    f"critic_{candidate.hook_type}_r{round_no}",
                )
                review_text = critique.get("review", "")
                candidate.retention_notes.append(f"critic_round_{round_no}: {review_text[:500]}")

                if not gate["passed"] or review_text.strip():
                    rewritten = self._run_stage(
                        3,
                        lambda c=candidate, r=review_text: self.agents.rewrite_from_critique(
                            c.text, r, self.state.analysis, self.state.audience
                        ),
                        f"rewrite_{candidate.hook_type}_r{round_no}",
                    )
                    if rewritten and rewritten != candidate.text:
                        candidate.text = rewritten
                        candidate.iteration += 1
                        changed = True

                candidate.text = self.retention._clean(candidate.text)

            self.state.checkpoints[f"critic_round_{round_no}"] = {
                "changed": changed,
                "candidate_count": len(self.state.candidates),
            }
            if not changed:
                break

        self._checkpoint(3)

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
            quality_report=self.state.checkpoints,
        )

    def _explain(self, winner, analysis):
        if not winner:
            return "لم يتم العثور على هوك مناسب."
        score = winner.score.total if winner.score else 0
        return (
            f"الهوك الفائز مبني على زاوية {winner.hook_type}. "
            f"مرّ على تحليل السكريبت ثم الكتابة والنقد وإعادة الصياغة وبوابة الجودة. "
            f"الهدف هو فتح فجوة فضول حقيقية وربط البداية بأقوى نقطة في المحتوى. "
            f"التقييم النهائي: {score:.1f}/100."
        )

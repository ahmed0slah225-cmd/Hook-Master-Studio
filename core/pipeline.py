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
    """Multi-stage hook factory with resumable checkpoints and hard final quality gates."""

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

        if self.state.completed and self.state.winner is not None:
            return self._result()

        if self.state.analysis is None:
            self.state.analysis = self._run_stage(
                1,
                lambda: self.analyzer.analyze(self.state.script, self.state.audience, self.state.style),
                "analysis",
            )

        if not self.state.candidates:
            self.state.candidates = self._run_stage(
                2,
                lambda: self.agents.generate_candidates(
                    self.state.analysis, self.state.script, self.state.audience, self.state.style
                ),
                "generation",
            )

        self.state.candidates = self.retention.refine_candidates(self.state.candidates, self.state.analysis)

        critic_done = any(k.startswith("completed_rewrite_round_") for k in self.state.checkpoints)
        if not critic_done:
            self._critic_loop()

        if any(candidate.score is None for candidate in self.state.candidates):
            self.state.candidates = self._run_stage(
                3,
                lambda: self.scorer.score_batch(
                    self.state.candidates, self.state.analysis, self.state.audience
                ),
                "batch_scoring",
            )
        self._checkpoint(3)

        accepted, rejected = self.quality_gate.filter(self.state.candidates, self.state.analysis)

        # A rejected hook is never promoted as a fallback. This is intentional:
        # a polished but structurally weak opener must not beat a real hook.
        pool = accepted
        self.state.winner = self.selector.select(pool, self.state.analysis)
        if self.state.winner:
            self.state.winner = self.retention.final_polish(self.state.winner, self.state.analysis)

        experiment = self.ab_tester.compare(pool)
        self.state.checkpoints["quality_gate"] = {
            "accepted": len(accepted),
            "rejected": len(rejected),
            "rejected_types": [c.hook_type for c in rejected],
            "rejected_reasons": {
                c.hook_type: self.quality_gate.evaluate(c, self.state.analysis)["flags"]
                for c in rejected
            },
        }
        self.state.checkpoints["ab_test"] = experiment.__dict__ if experiment else None

        if self.state.winner is None:
            self.state.checkpoints["no_winner"] = True
            self.state.completed = False
            raise RuntimeError(
                "لم ينجح أي هوك في بوابة الجودة. تم منع اختيار هوك ضعيف تلقائيًا؛ أعد المحاولة لإعادة توليد الهوكات."
            )

        self.state.completed = True
        self._checkpoint(5)
        return self._result()

    def _run_stage(self, stage: int, operation: Callable[[], Any], label: str):
        """Retry only the failed operation; completed stages are never repeated on resume."""
        assert self.state is not None
        last = None
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            try:
                result = operation()
                self.state.checkpoints[f"{label}_attempts"] = attempt
                self.state.checkpoints[f"completed_{label}"] = True
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
            local_flags = []
            for index, candidate in enumerate(self.state.candidates):
                gate = self.quality_gate.evaluate(candidate, self.state.analysis)
                local_flags.append({"index": index, "passed": gate["passed"], "flags": gate["flags"]})

            reviews = self._run_stage(
                3,
                lambda: self.agents.critique_candidates(
                    self.state.candidates, self.state.script, self.state.analysis
                ),
                f"critic_round_{round_no}",
            )

            for review in reviews:
                if not isinstance(review, dict):
                    continue
                try:
                    index = int(review.get("index"))
                    candidate = self.state.candidates[index]
                except (ValueError, TypeError, IndexError):
                    continue
                candidate.retention_notes.append(
                    f"critic_round_{round_no}: "
                    f"{review.get('rewrite_direction', '')} "
                    f"issues={review.get('issues', [])}"
                )

            before = [c.text for c in self.state.candidates]
            self.state.candidates = self._run_stage(
                3,
                lambda: self.agents.rewrite_candidates(
                    self.state.candidates, reviews, self.state.analysis, self.state.audience
                ),
                f"rewrite_round_{round_no}",
            )
            changed = before != [c.text for c in self.state.candidates]
            self.state.checkpoints[f"critic_round_{round_no}_local_flags"] = local_flags
            self.state.checkpoints[f"critic_round_{round_no}"] = {
                "changed": changed,
                "candidate_count": len(self.state.candidates),
                "reviews": len(reviews),
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
            f"تم اختباره كسبب للمشاهدة، ثم مرّ على النقد، إعادة الصياغة، "
            f"وبوابة الجودة قبل الاختيار. التقييم النهائي: {score:.1f}/10."
        )

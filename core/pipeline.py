from config.models import PipelineState, HookResult
from utils.api import GeminiService
from utils.retry import retry_transient
from .script_analyzer import ScriptAnalyzer
from .hook_engine import HookEngine
from .scoring_engine import ScoringEngine
from .hook_selector import HookSelector

class HookPipeline:
    def __init__(self, settings):
        self.settings = settings
        self.ai = GeminiService(settings)
        self.analyzer = ScriptAnalyzer(self.ai)
        self.generator = HookEngine(self.ai)
        self.scorer = ScoringEngine(self.ai)
        self.selector = HookSelector()
        self.state = None

    def run(self, script, audience, duration, style):
        self.state = PipelineState(script=script, audience=audience, duration=duration, style=style, stage=0)
        self.state.analysis = self.analyzer.analyze(script, audience, style); self.state.stage = 1
        candidates = self.generator.generate(self.state.analysis, script, audience, style); self.state.candidates = candidates; self.state.stage = 2
        for c in self.state.candidates:
            c.score = self.scorer.score(c, self.state.analysis, audience)
        self.state.stage = 3
        self.state.winner = self.selector.select(self.state.candidates); self.state.completed = True; self.state.stage = 4
        explanation = self._explain(self.state.winner, self.state.analysis)
        return HookResult(analysis=self.state.analysis, candidates=self.state.candidates, winner=self.state.winner, explanation=explanation)

    def resume(self, state):
        self.state = PipelineState.model_validate(state)
        if self.state.analysis is None:
            self.state.analysis = self.analyzer.analyze(self.state.script, self.state.audience, self.state.style); self.state.stage = 1
        if not self.state.candidates:
            self.state.candidates = self.generator.generate(self.state.analysis, self.state.script, self.state.audience, self.state.style); self.state.stage = 2
        for c in self.state.candidates:
            if c.score is None: c.score = self.scorer.score(c, self.state.analysis, self.state.audience)
        self.state.winner = self.selector.select(self.state.candidates); self.state.completed = True; self.state.stage = 4
        return HookResult(analysis=self.state.analysis, candidates=self.state.candidates, winner=self.state.winner, explanation=self._explain(self.state.winner, self.state.analysis))

    def _explain(self, winner, analysis):
        if not winner: return "لم يتم العثور على هوك مناسب."
        return f"الهوك الفائز اختار زاوية {winner.hook_type} لأنها مرتبطة مباشرة بأقوى نقطة في السكريبت: {analysis.unique_angle or analysis.core_problem}."

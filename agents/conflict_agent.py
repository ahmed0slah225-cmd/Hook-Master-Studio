from .base_agent import BaseAgent
class ConflictAgent(BaseAgent):
    name = "conflict_detector"
    def detect(self, script):
        return self.ask(f"ابحث عن التناقض المركزي في السكريبت: شيء يفعله الناس ويعتقدون أنه صحيح بينما النص يوضح زاوية مختلفة.\n{script}")

from .base_agent import BaseAgent
class CuriosityAgent(BaseAgent):
    name = "curiosity_gap"
    def discover(self, script):
        return self.ask(f"اكتشف الأسئلة التي سيظل المشاهد يريد معرفة إجاباتها بعد قراءة السكريبت. حوّلها إلى فجوات فضول حقيقية وليست clickbait.\n{script}")

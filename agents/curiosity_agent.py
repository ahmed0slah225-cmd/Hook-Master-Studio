from .base_agent import BaseAgent

class CuriosityAgent(BaseAgent):
    name = "curiosity_architect"

    def analyze(self, script, previous_context):
        return self.ask(f"استخرج أقوى سؤال لم يُجب عنه السكريبت في بدايته، والذي يمكن أن يصنع فجوة فضول صادقة. لا تستخدم clickbait. ابنِ على السياق السابق:\n{previous_context}\nالسكريبت:\n{script}")

    def discover(self, script):
        return self.ask(f"اكتشف الأسئلة التي سيظل المشاهد يريد معرفة إجاباتها بعد قراءة السكريبت. حوّلها إلى فجوات فضول حقيقية وليست clickbait.\n{script}")

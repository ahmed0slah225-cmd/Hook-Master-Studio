from .base_agent import BaseAgent
class PainAgent(BaseAgent):
    name = "pain_detector"
    def extract(self, script):
        return self.ask(f"استخرج المشكلة الإنسانية الحقيقية من السكريبت، بصياغة يفهمها شخص عادي من غير مصطلحات أكاديمية.\n{script}")

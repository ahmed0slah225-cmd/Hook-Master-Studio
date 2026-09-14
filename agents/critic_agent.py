from .base_agent import BaseAgent
class CriticAgent(BaseAgent):
    name = "critic"
    def review(self, hook, script):
        return self.ask(f"انتقد الهوك التالي من منظور مشاهد يوتيوب، وابحث عن الكذب، العمومية، ضعف الفضول والتصنع. لا تعيد كتابته الآن.\nHOOK: {hook}\nSCRIPT: {script}")

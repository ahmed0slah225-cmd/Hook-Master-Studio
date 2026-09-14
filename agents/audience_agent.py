from .base_agent import BaseAgent
class AudienceAgent(BaseAgent):
    name = "viewer_psychology"
    def profile(self, script, audience):
        return self.ask(f"حدد ما الذي يخشاه المشاهد أو يريده أو يشعر به أثناء مشاهدة هذا الموضوع. الجمهور: {audience}. لا تضف معلومات خارج السكريبت.\n{script}")

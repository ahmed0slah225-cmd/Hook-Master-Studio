from .base_agent import BaseAgent
class HumanizerAgent(BaseAgent):
    name = "egyptian_humanizer"
    def rewrite(self, hook):
        return self.ask(f"حوّل الهوك إلى كلام مصري طبيعي كأنه خارج من شخص بيتكلم، بدون تغيير الفكرة، وبدون مبالغة أو جمل AI مصقولة. حافظ على الفضول.\n{hook}")

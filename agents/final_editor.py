from .base_agent import BaseAgent
class FinalEditor(BaseAgent):
    name = "final_editor"
    def polish(self, hook, audience):
        return self.ask(f"راجع هذا الهوك كآخر محرر قبل التصوير. حافظ على المعنى، اجعله مصريًا طبيعيًا، واحذف أي كلمة تبدو مصطنعة أو تسويقية. الجمهور: {audience}.\n{hook}")

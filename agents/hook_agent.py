from .base_agent import BaseAgent
class HookAgent(BaseAgent):
    name = "hook_writer"
    def build(self, analysis, hook_type, audience):
        return self.ask(f"اكتب Hook مصري طبيعي من نوع {hook_type} للجمهور {audience}. استخدم التحليل التالي دون اختراع: {analysis.model_dump_json()}")

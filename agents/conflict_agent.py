from .base_agent import BaseAgent

class ConflictAgent(BaseAgent):
    name = "conflict_detector"

    def analyze(self, script, previous_context):
        return self.ask(f"استخرج التناقض أو الصراع الذي يمكن أن يوقف المشاهد ذهنيًا. لا تخترع حقائق. استخدم كل ما خرج من الوكلاء السابقين:\n{previous_context}\nالسكريبت:\n{script}")

    def detect(self, script):
        return self.ask(f"ابحث عن التناقض المركزي في السكريبت: شيء يفعله الناس ويعتقدون أنه صحيح بينما النص يوضح زاوية مختلفة.\n{script}")

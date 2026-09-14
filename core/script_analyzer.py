import json
from config.models import ScriptAnalysis
from utils.api import GeminiService
from utils.retry import retry_transient

class ScriptAnalyzer:
    def __init__(self, ai: GeminiService): self.ai = ai
    def analyze(self, script, audience, style):
        prompt = f'''أنت محلل محتوى يوتيوب محترف. حلل السكريبت التالي قبل كتابة أي هوك.
الجمهور: {audience}\nالأسلوب: {style}
استخرج: premise, core_problem, promise, strongest_moments, emotional_triggers, conflicts, curiosity_gaps, transformation, unique_angle, audience.
لا تخترع معلومات. أعد JSON فقط بالمفاتيح نفسها.
SCRIPT:\n{script}'''
        data = retry_transient(lambda: self.ai.generate_json(prompt))
        return ScriptAnalysis.model_validate(data)

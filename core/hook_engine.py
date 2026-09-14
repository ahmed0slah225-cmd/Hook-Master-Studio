from config.constants import HOOK_TYPES
from config.models import HookCandidate
from utils.retry import retry_transient

class HookEngine:
    def __init__(self, ai): self.ai = ai
    def generate(self, analysis, script, audience, style):
        types = ", ".join(HOOK_TYPES)
        prompt = f'''أنت كاتب Hooks محترف لفيديوهات يوتيوب. ابنِ 8 مرشحين، واحد لكل نوع: {types}.
الهوك لازم يكون مصممًا من أقوى نقطة في السكريبت، مصري طبيعي، مفهوم، فيه سبب حقيقي للاستمرار، وليس clickbait كاذب.
تجنب: أهلا بكم، في فيديو النهارده، كلام عام، نصائح مباشرة، المبالغة، الجمل القصيرة الفارغة.
أعد JSON array بعناصر: text, hook_type, rationale.
تحليل السكريبت: {analysis.model_dump_json()}\nالسكريبت:\n{script}\nالجمهور: {audience}\nالستايل: {style}'''
        data = retry_transient(lambda: self.ai.generate_json(prompt))
        if isinstance(data, dict): data = data.get("candidates", [])
        return [HookCandidate.model_validate(x) for x in data]

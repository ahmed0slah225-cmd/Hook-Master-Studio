from .base_agent import BaseAgent

class PainAgent(BaseAgent):
    name = "pain_mapper"

    def analyze(self, script, topic_context, viewer_context):
        return self.ask(f"حدد الألم أو الموقف اليومي الأكثر قابلية للتعاطف داخل السكريبت. لا تضف قصة من عندك. ابنِ على مخرجات الوكيلين السابقين. تحليل الموضوع:\n{topic_context}\nرؤية المشاهد:\n{viewer_context}\nالسكريبت:\n{script}")

    def extract(self, script):
        return self.ask(f"استخرج المشكلة الإنسانية الحقيقية من السكريبت، بصياغة يفهمها شخص عادي من غير مصطلحات أكاديمية.\n{script}")

from .base_agent import BaseAgent

class ViewerAgent(BaseAgent):
    name = "viewer_psychologist"

    def analyze(self, script, topic_context, audience):
        return self.ask(f"أنت مشاهد من الجمهور المستهدف. استخرج ما الذي سيجعلك تكمل أول 30 ثانية، وما الذي سيجعلك تخرج. استخدم تحليل الموضوع السابق ولا تكتب هوك. الجمهور: {audience}\nتحليل الموضوع:\n{topic_context}\nالسكريبت:\n{script}")

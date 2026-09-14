from .base_agent import BaseAgent

class TopicAgent(BaseAgent):
    name = "topic_strategist"

    def analyze(self, script):
        return self.ask(f"حلل السكريبت كموضوع يوتيوب. استخرج الفكرة المركزية، التناقض الأساسي، وما الذي يجعل الموضوع يستحق المشاهدة. لا تكتب هوك. السكريبت:\n{script}")

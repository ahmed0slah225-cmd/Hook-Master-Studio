class BaseAgent:
    name = "base"
    def __init__(self, ai): self.ai = ai
    def ask(self, prompt): return self.ai.generate(prompt)

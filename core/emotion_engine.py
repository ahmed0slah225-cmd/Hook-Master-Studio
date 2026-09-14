class EmotionEngine:
    SIGNALS = ["fear", "relief", "recognition", "surprise", "frustration", "hope", "curiosity"]
    def inspect(self, analysis):
        text = " ".join(analysis.emotional_triggers).lower()
        return {signal: signal in text for signal in self.SIGNALS}

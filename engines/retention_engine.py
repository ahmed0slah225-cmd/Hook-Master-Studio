class RetentionEngine:
    def inspect(self, hook: str):
        words = hook.split()
        return {
            "word_count": len(words),
            "has_question": "؟" in hook or "?" in hook,
            "has_open_loop": any(x in hook for x in ["بس", "المشكلة", "والغريب", "اللي محدش"]),
            "density": round(min(1.0, len(words) / 35), 2),
        }

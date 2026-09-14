class HookSelector:
    def select(self, candidates):
        if not candidates: return None
        return max(candidates, key=lambda c: c.score.total if c.score else 0)

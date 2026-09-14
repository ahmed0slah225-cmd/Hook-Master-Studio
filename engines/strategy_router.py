from config.constants import HOOK_TYPES
class StrategyRouter:
    """Maps content conditions to complementary hook strategies."""
    def route(self, analysis):
        routes = list(HOOK_TYPES)
        if analysis.conflicts: routes.insert(0, "conflict")
        if analysis.strongest_moments: routes.insert(0, "story")
        return list(dict.fromkeys(routes))

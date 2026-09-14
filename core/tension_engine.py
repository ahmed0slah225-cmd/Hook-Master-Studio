class TensionEngine:
    def build(self, analysis):
        return {
            "problem": analysis.core_problem,
            "conflict": analysis.conflicts[0] if analysis.conflicts else "",
            "promise": analysis.promise,
            "transformation": analysis.transformation,
        }

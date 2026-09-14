class CuriosityEngine:
    def gaps(self, analysis):
        gaps = list(analysis.curiosity_gaps)
        gaps.extend(analysis.conflicts)
        if analysis.unique_angle: gaps.append(analysis.unique_angle)
        return list(dict.fromkeys(x for x in gaps if x))

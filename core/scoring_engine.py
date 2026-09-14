from config.models import HookScore
from config.constants import SCORE_DIMENSIONS
from utils.retry import retry_transient

class ScoringEngine:
    def __init__(self, ai): self.ai = ai
    def score(self, candidate, analysis, audience):
        prompt = f'''قيّم هذا الهوك كخبير Retention. لا تجامل. أعط درجات 0-10 للأبعاد: {', '.join(SCORE_DIMENSIONS)}.
ثم strengths و weaknesses. total متوسط موزون: retention 20%, curiosity 18%, clarity 15%, emotion 12%, specificity 10%, tension 10%, credibility 5%, naturalness 10%.
أعد JSON فقط. الهوك: {candidate.text}\nالتحليل: {analysis.model_dump_json()}\nالجمهور: {audience}'''
        data = retry_transient(lambda: self.ai.generate_json(prompt))
        return HookScore.model_validate(data)

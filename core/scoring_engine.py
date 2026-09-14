from config.models import HookScore
from config.constants import SCORE_DIMENSIONS
from utils.retry import retry_transient


class ScoringEngine:
    def __init__(self, ai):
        self.ai = ai

    def score(self, candidate, analysis, audience):
        prompt = f'''قيّم هذا الهوك كخبير Retention. لا تجامل. أعط درجات 0-10 للأبعاد: {', '.join(SCORE_DIMENSIONS)}.
ثم strengths و weaknesses. total متوسط موزون: retention 20%, curiosity 18%, clarity 15%, emotion 12%, specificity 10%, tension 10%, credibility 5%, naturalness 10%.
أعد JSON فقط. الهوك: {candidate.text}\nالتحليل: {analysis.model_dump_json()}\nالجمهور: {audience}'''
        data = retry_transient(lambda: self.ai.generate_json(prompt))
        return HookScore.model_validate(data)

    def score_batch(self, candidates, analysis, audience):
        """Score the whole candidate pool in one model call."""
        payload = [
            {"index": i, "hook_type": c.hook_type, "text": c.text}
            for i, c in enumerate(candidates)
        ]
        prompt = f'''
أنت لجنة تقييم هوكات يوتيوب.
قيّم كل هوك من 0 إلى 10 في الأبعاد التالية: {', '.join(SCORE_DIMENSIONS)}.
احسب total باستخدام الأوزان: retention 20%, curiosity 18%, clarity 15%, emotion 12%, specificity 10%, tension 10%, credibility 5%, naturalness 10%.
لا تجامل، واذكر strengths و weaknesses و risk_flags.

التحليل:
{analysis.model_dump_json()}
الجمهور: {audience}
الهوكات:
{payload}

أعد JSON array فقط:
{{"index":0,"total":8.2,"dimensions":{{"clarity":8,"curiosity":9,"specificity":7,"emotion":8,"tension":8,"credibility":9,"retention":9,"naturalness":8}},"strengths":[],"weaknesses":[],"risk_flags":[]}}
'''
        data = retry_transient(lambda: self.ai.generate_json(prompt))
        if isinstance(data, dict):
            data = data.get("scores", data.get("candidates", []))
        if not isinstance(data, list):
            raise ValueError("Scoring model returned an invalid score list")

        for item in data:
            if not isinstance(item, dict):
                continue
            try:
                index = int(item.get("index"))
                candidates[index].score = HookScore.model_validate(item)
            except (ValueError, TypeError, IndexError):
                continue
        return candidates

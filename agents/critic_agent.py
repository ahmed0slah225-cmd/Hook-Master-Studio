from .base_agent import BaseAgent
from config.models import HookCandidate, ScriptAnalysis

class CriticAgent(BaseAgent):
    name = "critic"
    GENERIC = ["معلومات مهمة", "خليني أقولك", "النهاردة هنعرف", "في الفيديو ده"]

    def review(self, hook, script):
        return self.ask(
            f"انتقد الهوك التالي من منظور مشاهد يوتيوب. ابحث عن الكذب، العمومية، ضعف الفضول، التصنع، كشف الإجابة مبكراً، وغياب السبب الذي يجعل المشاهد يكمل. لا تعيد كتابته الآن.\nHOOK: {hook}\nSCRIPT: {script}"
        )

    def local_review(self, candidate: HookCandidate, analysis: ScriptAnalysis):
        issues = []
        text = candidate.text.strip()
        if len(text.split()) < 10:
            issues.append("قصير لدرجة لا يبني فضولاً كافياً")
        if any(x in text for x in self.GENERIC):
            issues.append("لغة افتتاحية عامة ومستهلكة")
        if candidate.hook_type == "problem-driven" and analysis.core_problem:
            if not any(word in text for word in analysis.core_problem.split()[:4]):
                issues.append("الهوك لا يرتبط بوضوح كافٍ بالمشكلة المركزية")
        return {
            "approved": not issues,
            "issues": issues,
            "rewrite_direction": "اربط الهوك بتفصيلة محددة وافتح سؤالاً لا يُجاب عنه فوراً." if issues else "حافظ على الزاوية ولا تزود الزخرفة."
        }

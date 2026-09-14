from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ScriptAnalysis(BaseModel):
    title_or_premise: str = ""
    core_problem: str = ""
    audience: str = ""
    promise: str = ""
    strongest_moments: List[str] = Field(default_factory=list)
    emotional_triggers: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    curiosity_gaps: List[str] = Field(default_factory=list)
    transformation: str = ""
    unique_angle: str = ""

class HookScore(BaseModel):
    total: float = 0
    dimensions: Dict[str, float] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)

class HookCandidate(BaseModel):
    text: str
    hook_type: str
    rationale: str = ""
    score: Optional[HookScore] = None

class HookResult(BaseModel):
    analysis: ScriptAnalysis
    candidates: List[HookCandidate] = Field(default_factory=list)
    winner: Optional[HookCandidate] = None
    explanation: str = ""

class PipelineState(BaseModel):
    script: str
    audience: str
    duration: int
    style: str
    stage: int = 0
    analysis: Optional[ScriptAnalysis] = None
    candidates: List[HookCandidate] = Field(default_factory=list)
    winner: Optional[HookCandidate] = None
    completed: bool = False

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

class ScriptAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
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
    stakes: str = ""
    hidden_question: str = ""
    likely_objections: List[str] = Field(default_factory=list)
    proof_points: List[str] = Field(default_factory=list)
    forbidden_angles: List[str] = Field(default_factory=list)

class HookScore(BaseModel):
    total: float = 0
    dimensions: Dict[str, float] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)

class HookCandidate(BaseModel):
    text: str
    hook_type: str
    rationale: str = ""
    score: Optional[HookScore] = None
    retention_notes: List[str] = Field(default_factory=list)
    humanized: bool = False
    iteration: int = 0

class HookResult(BaseModel):
    analysis: ScriptAnalysis
    candidates: List[HookCandidate] = Field(default_factory=list)
    winner: Optional[HookCandidate] = None
    explanation: str = ""
    quality_report: Dict[str, Any] = Field(default_factory=dict)

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
    attempts: int = 0
    errors: List[str] = Field(default_factory=list)
    checkpoints: Dict[str, Any] = Field(default_factory=dict)

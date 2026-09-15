from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list, tuple)):
        try:
            if isinstance(value, dict):
                readable = []
                for key, item in value.items():
                    readable.append(f"{key}: {_coerce_text(item)}")
                return " — ".join(readable)
            return " — ".join(_coerce_text(item) for item in value)
        except Exception:
            try:
                return json.dumps(value, ensure_ascii=False)
            except Exception:
                return str(value)
    return str(value)


def _coerce_text_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [_coerce_text(item) for item in value if item is not None]
    return [_coerce_text(value)]


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

    _string_fields = field_validator(
        "title_or_premise", "core_problem", "audience", "promise", "transformation",
        "unique_angle", "stakes", "hidden_question", mode="before"
    )(_coerce_text)

    _list_fields = field_validator(
        "strongest_moments", "emotional_triggers", "conflicts", "curiosity_gaps",
        "likely_objections", "proof_points", "forbidden_angles", mode="before"
    )(_coerce_text_list)


class HookScore(BaseModel):
    total: float = 0
    dimensions: Dict[str, float] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)

    @field_validator("total", mode="before")
    @classmethod
    def _coerce_total(cls, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @field_validator("dimensions", mode="before")
    @classmethod
    def _coerce_dimensions(cls, value: Any) -> Dict[str, float]:
        if not isinstance(value, dict):
            return {}
        result: Dict[str, float] = {}
        for key, raw in value.items():
            try:
                result[str(key)] = float(raw)
            except (TypeError, ValueError):
                continue
        return result

    _text_lists = field_validator("strengths", "weaknesses", "risk_flags", mode="before")(_coerce_text_list)


class HookCandidate(BaseModel):
    text: str
    hook_type: str
    rationale: str = ""
    score: Optional[HookScore] = None
    retention_notes: List[str] = Field(default_factory=list)
    humanized: bool = False
    iteration: int = 0

    _candidate_text = field_validator("text", "hook_type", "rationale", mode="before")(_coerce_text)
    _retention_notes = field_validator("retention_notes", mode="before")(_coerce_text_list)


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

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import uuid


@dataclass(frozen=True)
class ActionPlan:
    """Immutable action plan for a package operation."""

    package: str
    action: str
    adb_command: str
    restore_command: str
    recommendation: str
    confidence: str
    evidence: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    preconditions: List[str] = field(default_factory=list)
    estimated_impact: str = "unknown"
    requires_confirmation: bool = True
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))


def create_action_plan(package_name, recommendation):
    """Create an immutable action plan for disabling a package."""

    package = (package_name or "").strip()
    recommendation_value = (recommendation or "unknown").strip().lower()

    if not package:
        raise ValueError("package_name is required")

    if recommendation_value not in {"safe", "review", "critical", "unknown"}:
        recommendation_value = "unknown"

    confidence = "high" if recommendation_value == "safe" else "medium"
    if recommendation_value == "unknown":
        confidence = "low"

    evidence = [
        f"Recommendation received: {recommendation_value}",
        "Planner created plan without executing ADB commands",
    ]

    warnings = []
    preconditions = [
        "Package name is provided",
        "User confirmation is required before execution",
    ]

    estimated_impact = "low"
    if recommendation_value in {"review", "critical"}:
        estimated_impact = "medium"
    if recommendation_value == "critical":
        estimated_impact = "high"

    if recommendation_value == "critical":
        warnings.append("Package is marked as critical; review carefully before execution")
    elif recommendation_value == "review":
        warnings.append("Package requires review before execution")

    adb_command = f"pm disable-user --user 0 {package}"
    restore_command = f"pm enable {package}"

    return ActionPlan(
        package=package,
        action="disable",
        adb_command=adb_command,
        restore_command=restore_command,
        recommendation=recommendation_value,
        confidence=confidence,
        evidence=evidence,
        warnings=warnings,
        preconditions=preconditions,
        estimated_impact=estimated_impact,
        requires_confirmation=True,
        execution_id=str(uuid.uuid4()),
    )

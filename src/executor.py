from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone

from planner import ActionPlan


@dataclass(frozen=True)
class ActionResult:
    """Result of executing a package action plan."""

    package: str
    action: str
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    timestamp: str


def execute_action_plan(plan: ActionPlan) -> ActionResult:
    """Execute a disable action plan through adb and return structured results."""

    if not isinstance(plan, ActionPlan):
        raise TypeError("plan must be an ActionPlan instance")

    action = (plan.action or "").strip().lower()
    if action != "disable":
        raise ValueError("Only disable actions are supported")

    package = (plan.package or "").strip()
    if not package:
        raise ValueError("plan.package is required")

    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        completed = subprocess.run(
            ["adb", "shell", "pm", "disable-user", "--user", "0", package],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        return ActionResult(
            package=package,
            action=action,
            success=False,
            exit_code=-1,
            stdout="",
            stderr=str(exc),
            timestamp=timestamp,
        )

    return ActionResult(
        package=package,
        action=action,
        success=completed.returncode == 0,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        timestamp=timestamp,
    )

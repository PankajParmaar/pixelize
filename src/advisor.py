import json
from functools import lru_cache
from pathlib import Path


_REPORTS_PATH = Path(__file__).resolve().parent.parent / "reports"
_KNOWLEDGE_CANDIDATES_PATH = _REPORTS_PATH / "knowledge_candidates.json"

from classifier import classify_package
from snapshot_loader import SnapshotValidationError, load_snapshot


_KNOWLEDGE_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "package_knowledge.json"


def _load_package_knowledge():
    """Load package knowledge once per process execution."""

    if not _KNOWLEDGE_PATH.exists():
        return {}

    with _KNOWLEDGE_PATH.open("r", encoding="utf-8") as handle:
        entries = json.load(handle)

    return {entry["package"]: entry for entry in entries if "package" in entry}


_PACKAGE_KNOWLEDGE = _load_package_knowledge()


@lru_cache(maxsize=1)
def _get_snapshot_package_sets():
    """Return snapshot-backed package sets once per process execution."""

    snapshot_path = Path(__file__).resolve().parent.parent / "snapshots" / "iqoo13_2026-06-28.json"
    try:
        snapshot = load_snapshot(snapshot_path)
    except (FileNotFoundError, SnapshotValidationError):
        return set(), set()

    return set(snapshot.system_packages), set(snapshot.user_packages)


def _get_package_name(package_entry):
    """Extract a package name from either a metadata dict or a plain string."""

    if isinstance(package_entry, dict):
        return package_entry.get("package") or package_entry.get("name")

    return package_entry


def _is_system_package(package_entry, system_packages, user_packages):
    """Determine whether a package should be considered a system package using snapshot metadata."""

    package_name = _get_package_name(package_entry)
    if not package_name:
        return False

    if isinstance(package_entry, dict):
        if "system" in package_entry:
            return bool(package_entry["system"])
        if "user" in package_entry:
            return not bool(package_entry["user"])

    return package_name in system_packages and package_name not in user_packages


def _build_recommendation(package, recommendation, confidence, reason, source):
    """Create a structured recommendation object."""

    return {
        "package": package,
        "recommendation": recommendation,
        "confidence": confidence,
        "reason": reason,
        "source": source,
    }


def _recommend_from_knowledge(package):
    """Return an enriched recommendation entry from the knowledge base if available."""

    entry = _PACKAGE_KNOWLEDGE.get(package)
    if not entry:
        return None

    recommendation = entry.get("recommendation", "unknown")
    if recommendation not in {"safe", "review", "critical"}:
        return None

    return _build_recommendation(
        package=package,
        recommendation=recommendation,
        confidence=entry.get("confidence", "low"),
        reason=entry.get("reason", "Knowledge base entry"),
        source="knowledge",
    )


def _write_knowledge_candidates(unknown_packages):
    """Write unknown packages to a JSON file that can be copied into the knowledge base."""

    _REPORTS_PATH.mkdir(parents=True, exist_ok=True)
    candidates = [
        {
            "package": item["package"],
            "recommendation": "unknown",
            "confidence": "low",
            "reason": "",
            "notes": [],
        }
        for item in unknown_packages
    ]

    with _KNOWLEDGE_CANDIDATES_PATH.open("w", encoding="utf-8") as handle:
        json.dump(candidates, handle, indent=2)
        handle.write("\n")


def get_debloat_recommendations(packages):
    """Prototype debloat recommendations based on snapshot-backed system package metadata."""

    safe = []
    review = []
    critical = []
    unknown = []
    system_packages, user_packages = _get_snapshot_package_sets()

    for package_entry in packages:
        package_name = _get_package_name(package_entry)
        if not package_name:
            continue

        if not _is_system_package(package_entry, system_packages, user_packages):
            continue

        if package_name in _PACKAGE_KNOWLEDGE:
            knowledge_recommendation = _recommend_from_knowledge(package_name)
            if knowledge_recommendation is not None:
                bucket = knowledge_recommendation["recommendation"]
                if bucket == "safe":
                    safe.append(knowledge_recommendation)
                elif bucket == "review":
                    review.append(knowledge_recommendation)
                else:
                    critical.append(knowledge_recommendation)
                continue

        unknown.append({
            "package": package_name,
            "reason": "No knowledge base entry.",
        })

        category = classify_package(package_name)
        if category in {"Android", "Qualcomm"}:
            recommendation = _build_recommendation(
                package=package_name,
                recommendation="critical",
                confidence="low",
                reason="Prototype heuristic",
                source="prototype",
            )
            critical.append(recommendation)
        elif category in {"Google", "vivo"}:
            recommendation = _build_recommendation(
                package=package_name,
                recommendation="review",
                confidence="low",
                reason="Prototype heuristic",
                source="prototype",
            )
            review.append(recommendation)
        else:
            recommendation = _build_recommendation(
                package=package_name,
                recommendation="safe",
                confidence="low",
                reason="Prototype heuristic",
                source="prototype",
            )
            safe.append(recommendation)

    _write_knowledge_candidates(unknown)

    return {
        "safe": safe,
        "review": review,
        "critical": critical,
        "unknown": unknown,
    }

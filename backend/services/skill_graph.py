import json
import os
from collections import deque
from pathlib import Path

# Load skill graph data
_DATA_PATH = Path(__file__).parent.parent / "data" / "skill_graph_data.json"

with open(_DATA_PATH, "r") as f:
    SKILL_GRAPH: dict[str, list[str]] = json.load(f)

# Build reverse index for faster lookup
_SKILL_LOWER = {k.lower(): k for k in SKILL_GRAPH}


def normalize_skill(skill: str) -> str | None:
    """Return canonical skill name or None if not in graph."""
    return _SKILL_LOWER.get(skill.strip().lower())


def get_all_skills() -> list[str]:
    return list(SKILL_GRAPH.keys())


def get_neighbors(skill: str) -> list[str]:
    canonical = normalize_skill(skill)
    if not canonical:
        return []
    return SKILL_GRAPH.get(canonical, [])


def find_path(start: str, target: str) -> list[str] | None:
    """BFS path finder. Returns shortest path or None if unreachable."""
    start_canonical = normalize_skill(start)
    target_canonical = normalize_skill(target)

    if not start_canonical or not target_canonical:
        return None
    if start_canonical == target_canonical:
        return [start_canonical]

    visited = {start_canonical}
    queue = deque([[start_canonical]])

    while queue:
        path = queue.popleft()
        current = path[-1]

        for neighbor in SKILL_GRAPH.get(current, []):
            nb_canonical = normalize_skill(neighbor)
            if not nb_canonical:
                continue
            if nb_canonical == target_canonical:
                return path + [nb_canonical]
            if nb_canonical not in visited:
                visited.add(nb_canonical)
                queue.append(path + [nb_canonical])

    return None  # Skill gap too large


def is_reachable(from_skill: str, to_skill: str) -> bool:
    return find_path(from_skill, to_skill) is not None


def find_best_path(user_skills: list[str], target_skill: str) -> dict:
    """Find shortest path from any user skill to target. Returns path + source skill."""
    best = None
    best_source = None

    for us in user_skills:
        path = find_path(us, target_skill)
        if path and (best is None or len(path) < len(best)):
            best = path
            best_source = us

    if best:
        return {"path": best, "source": best_source, "reachable": True}
    return {"path": [], "source": None, "reachable": False}


def compute_confidence(path: list[str]) -> int:
    """Shorter path = higher confidence."""
    if not path:
        return 0
    length = len(path)
    if length == 1:
        return 100
    if length == 2:
        return 90
    if length == 3:
        return 75
    if length == 4:
        return 60
    if length == 5:
        return 45
    return max(20, 100 - (length * 15))


def compute_risk(path: list[str]) -> str:
    if not path:
        return "UNREACHABLE"
    length = len(path)
    if length <= 2:
        return "LOW"
    if length <= 3:
        return "MEDIUM"
    return "HIGH"

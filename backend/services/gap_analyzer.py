from services.skill_graph import find_best_path, compute_confidence, compute_risk


def analyze_gaps(user_skills: list[str], jd_skills: list[str]) -> dict:
    """
    Compare user skills vs JD skills.
    For each missing skill, find the best path using BFS on skill graph.
    Returns matched skills, missing skills, and gap analysis per missing skill.
    """
    user_set = set(user_skills)
    jd_set = set(jd_skills)

    matched = sorted(user_set & jd_set)
    missing = sorted(jd_set - user_set)

    gaps = []
    for target_skill in missing:
        result = find_best_path(user_skills, target_skill)
        path = result["path"]
        reachable = result["reachable"]
        confidence = compute_confidence(path) if reachable else 0
        risk = compute_risk(path) if reachable else "UNREACHABLE"

        gaps.append({
            "skill": target_skill,
            "path": path,
            "source_skill": result["source"],
            "reachable": reachable,
            "confidence": confidence,
            "risk": risk,
            "steps_needed": max(0, len(path) - 1),
            "message": (
                f"Learn via: {' → '.join(path)}" if reachable
                else "Skill gap too large — no clear path found"
            ),
        })

    # Sort: reachable first, then by confidence desc
    gaps.sort(key=lambda g: (-int(g["reachable"]), -g["confidence"]))

    match_score = round((len(matched) / len(jd_set)) * 100) if jd_set else 0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "gaps": gaps,
        "match_score": match_score,
        "total_required": len(jd_set),
        "total_matched": len(matched),
        "reachable_gaps": sum(1 for g in gaps if g["reachable"]),
        "unreachable_gaps": sum(1 for g in gaps if not g["reachable"]),
    }

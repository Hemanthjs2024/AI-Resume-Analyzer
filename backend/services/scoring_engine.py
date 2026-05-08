"""
Scoring Engine — Rule-based resume scoring across 4 dimensions.
No LLM required. Fully deterministic.
"""

import re

ACTION_VERBS = [
    "developed", "built", "designed", "implemented", "created", "led", "managed",
    "optimized", "improved", "reduced", "increased", "delivered", "launched",
    "architected", "deployed", "automated", "integrated", "refactored", "migrated",
    "collaborated", "mentored", "analyzed", "researched", "maintained", "scaled",
    "achieved", "drove", "established", "streamlined", "accelerated",
]

METRIC_PATTERNS = [
    re.compile(r"\d+\s*%"),           # percentage
    re.compile(r"\$[\d,]+"),          # dollar amounts
    re.compile(r"\d+[kK]\+?"),        # 10k+
    re.compile(r"[\d,]+\s*(?:users|customers|requests|transactions)"),
    re.compile(r"(?:reduced|increased|improved|decreased)\s+by\s+\d+"),
    re.compile(r"\d+x\s+(?:faster|better|improvement)"),
]

REQUIRED_SECTIONS = ["summary", "skills", "experience", "education"]
GOOD_SECTIONS = ["projects", "certifications", "achievements"]


def score_keyword_match(user_skills: list[str], jd_skills: list[str]) -> dict:
    if not jd_skills:
        return {"score": 0, "matched": [], "missing": [], "issues": ["No JD skills provided"], "fixes": []}
    matched = set(user_skills) & set(jd_skills)
    score = round((len(matched) / len(jd_skills)) * 100)
    issues = []
    fixes = []
    missing = set(jd_skills) - set(user_skills)
    if missing:
        issues.append(f"Missing {len(missing)} JD keywords: {', '.join(list(missing)[:5])}")
        fixes.append("Add missing keywords to your skills section (only if you know them).")
    return {"score": min(score, 100), "matched": list(matched), "missing": list(missing), "issues": issues, "fixes": fixes}


def score_impact(resume_text: str) -> dict:
    text_lower = resume_text.lower()
    verb_count = sum(1 for v in ACTION_VERBS if re.search(r'\b' + v + r'\b', text_lower))
    metric_count = sum(1 for p in METRIC_PATTERNS if p.search(resume_text))
    lines = [l.strip() for l in resume_text.split("\n") if l.strip()]
    bullet_count = sum(1 for l in lines if l.startswith(("•", "-", "–", "*")))

    verb_score = min(verb_count * 5, 50)
    metric_score = min(metric_count * 10, 30)
    bullet_score = min(bullet_count * 2, 20)
    total = verb_score + metric_score + bullet_score

    issues = []
    fixes = []
    if verb_count < 5:
        issues.append(f"Only {verb_count} action verbs found (aim for 10+).")
        fixes.append("Start bullet points with strong action verbs: Developed, Optimized, Led, Built.")
    if metric_count < 3:
        issues.append("Very few measurable metrics found.")
        fixes.append("Add quantified results: 'Reduced load time by 40%', 'Serving 10k+ users'.")
    if bullet_count < 5:
        issues.append("Too few bullet points in experience section.")
        fixes.append("Use bullet points to describe each responsibility/achievement.")

    return {"score": min(total, 100), "action_verb_count": verb_count, "metric_count": metric_count, "issues": issues, "fixes": fixes}


def score_format(resume_text: str, sections: dict) -> dict:
    score = 100
    issues = []
    fixes = []

    # Check email
    if not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text):
        score -= 15
        issues.append("No email address found.")
        fixes.append("Add your email address in the header section.")

    # Check phone
    if not re.search(r'[\+]?[\d\s\-\(\)]{10,}', resume_text):
        score -= 10
        issues.append("No phone number detected.")
        fixes.append("Include your phone number in the contact section.")

    # Length check
    word_count = len(resume_text.split())
    if word_count < 150:
        score -= 20
        issues.append("Resume appears too short (less than 150 words).")
        fixes.append("Expand experience descriptions and add more detail to projects.")
    elif word_count > 1200:
        score -= 10
        issues.append("Resume may be too long (ATS prefers concise resumes).")
        fixes.append("Trim to 1 page for <5 years experience, 2 pages max otherwise.")

    # No tables/images (can't detect from text, assume clean)
    # GitHub/LinkedIn detection
    if "github.com" not in resume_text.lower() and "linkedin.com" not in resume_text.lower():
        score -= 10
        issues.append("No GitHub or LinkedIn profile link found.")
        fixes.append("Add GitHub and LinkedIn URLs to your contact section.")

    return {"score": max(score, 0), "word_count": word_count, "issues": issues, "fixes": fixes}


def score_completeness(sections: dict) -> dict:
    score = 0
    issues = []
    fixes = []

    for sec in REQUIRED_SECTIONS:
        if sec in sections and len(sections[sec]) > 30:
            score += 20
        else:
            issues.append(f"Missing or too-short '{sec}' section.")
            fixes.append(f"Add a proper '{sec}' section with relevant content.")

    for sec in GOOD_SECTIONS:
        if sec in sections and len(sections[sec]) > 20:
            score += 5

    return {"score": min(score, 100), "present_sections": list(sections.keys()), "issues": issues, "fixes": fixes}


def score_education(resume_sections: dict, jd_requirements: dict) -> dict:
    score = 100
    issues = []
    fixes = []
    
    if not jd_requirements or jd_requirements.get("degree") == "Not specified":
        return {"score": 100, "issues": [], "fixes": []}

    target_degree = jd_requirements.get("degree", "").lower()
    target_majors = [m.lower() for m in jd_requirements.get("major", [])]
    
    edu_text = resume_sections.get("education", "").lower()
    
    # Check degree level (heuristic)
    degree_found = False
    if any(kw in target_degree for kw in ["bachelor", "b.s", "b.e"]):
        if any(kw in edu_text for kw in ["bachelor", "b.s", "b.e", "degree", "graduate", "computer science"]):
            degree_found = True
    elif any(kw in target_degree for kw in ["master", "m.s"]):
        if any(kw in edu_text for kw in ["master", "m.s", "postgraduate"]):
            degree_found = True
    else:
        # If no specific target degree found, assume ok if education section exists
        degree_found = True
            
    if not degree_found:
        score -= 30
        issues.append(f"Education level might not match {target_degree}.")
        fixes.append(f"Ensure your {target_degree} or equivalent qualification is highlighted.")

    # Check major
    if target_majors:
        major_found = any(m in edu_text for m in target_majors)
        if not major_found:
            score -= 20
            issues.append(f"Major mismatch. JD prefers {', '.join(target_majors)}.")
            fixes.append("Mention relevant coursework or specializations if your major is different.")

    return {"score": max(score, 0), "issues": issues, "fixes": fixes}


def calculate_overall_score(resume_text: str, sections: dict, user_skills: list, jd_data: dict, ai_score: int = None) -> dict:
    jd_skills = jd_data.get("required_skills", [])
    jd_edu = jd_data.get("education_requirements", {})
    
    kw = score_keyword_match(user_skills, jd_skills)
    impact = score_impact(resume_text)
    fmt = score_format(resume_text, sections)
    completeness = score_completeness(sections)
    edu = score_education(sections, jd_edu)

    # Weighted average (Deterministic)
    overall = round(
        kw["score"] * 0.30 +
        impact["score"] * 0.25 +
        edu["score"] * 0.20 +
        fmt["score"] * 0.15 +
        completeness["score"] * 0.10
    )

    # Holistic Match (Deterministic + AI)
    if ai_score is not None:
        # Give more weight to AI alignment (60%) vs technical rules (40%)
        holistic = round(overall * 0.4 + ai_score * 0.6)
    else:
        holistic = overall

    all_issues = kw["issues"] + impact["issues"] + fmt["issues"] + completeness["issues"]
    all_fixes = kw["fixes"] + impact["fixes"] + fmt["fixes"] + completeness["fixes"]

    grade = "A" if holistic >= 85 else "B" if holistic >= 70 else "C" if holistic >= 55 else "D"

    return {
        "overall_score": holistic,
        "base_score": overall,
        "ai_alignment_score": ai_score,
        "grade": grade,
        "breakdown": {
            "keyword_match": kw["score"],
            "impact_score": impact["score"],
            "format_score": fmt["score"],
            "completeness_score": completeness["score"],
        },
        "details": {
            "keyword_match": kw,
            "impact": impact,
            "format": fmt,
            "completeness": completeness,
            "education": edu,
        },
        "all_issues": (kw["issues"] + impact["issues"] + edu["issues"] + fmt["issues"] + completeness["issues"])[:10],
        "all_fixes": (kw["fixes"] + impact["fixes"] + edu["fixes"] + fmt["fixes"] + completeness["fixes"])[:10],
    }

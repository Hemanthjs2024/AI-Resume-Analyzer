"""
Resume Optimizer — Uses LLM client to rewrite resume sections.
Returns original vs optimized side-by-side for user review.
"""

from . import llm_client


def optimize_resume(sections: dict, jd_data: dict, user_skills: list[str]) -> list[dict]:
    """
    Optimize all resume sections.
    Returns list of {section, original, optimized} for user review.
    """
    job_title = jd_data.get("job_title", "Software Engineer")
    jd_skills = jd_data.get("required_skills", [])
    missing_skills = [s for s in jd_skills if s not in user_skills]

    # Handle specific sections
    handled_sections = ["header", "summary", "skills", "experience", "projects"]
    review_items = []
    
    # ── Summary ──────────────────────────────────────────────────────────────
    if "summary" in sections and sections["summary"].strip():
        original = sections["summary"]
        optimized = llm_client.optimize_summary(original, jd_skills)
        # Fallback to original if optimization fails
        if not optimized or not optimized.strip():
            optimized = original
        review_items.append({
            "section": "summary",
            "label": "Professional Summary",
            "original": original,
            "optimized": optimized,
            "status": "pending",
        })

    # ── Skills ───────────────────────────────────────────────────────────────
    if "skills" in sections and sections["skills"].strip():
        original = sections["skills"]
        optimized = llm_client.optimize_skills(original, missing_skills)
        # Fallback to original if optimization fails
        if not optimized or not optimized.strip():
            optimized = original
        review_items.append({
            "section": "skills",
            "label": "Technical Skills",
            "original": original,
            "optimized": optimized,
            "status": "pending",
        })

    # ── Experience ───────────────────────────────────────────────────────────
    if "experience" in sections and sections["experience"].strip():
        original = sections["experience"]
        optimized = llm_client.optimize_experience(original, job_title)
        # Fallback to original if optimization fails
        if not optimized or not optimized.strip():
            optimized = original
        review_items.append({
            "section": "experience",
            "label": "Work Experience",
            "original": original,
            "optimized": optimized,
            "status": "pending",
        })

    # ── Projects ─────────────────────────────────────────────────────────────
    if "projects" in sections and sections["projects"].strip():
        original = sections["projects"]
        review_items.append({
            "section": "projects",
            "label": "Projects",
            "original": original,
            "optimized": original,
            "status": "pending",
            "note": "Your selected strategic projects will be integrated here.",
        })

    # ── Include ALL other sections (Education, Certs, Achievements, etc.) ───
    for sec_key, content in sections.items():
        if sec_key in handled_sections or not content.strip():
            continue
            
        review_items.append({
            "section": sec_key,
            "label": sec_key.replace("_", " ").title(),
            "original": content,
            "optimized": content,
            "status": "accepted",
            "note": f"Original {sec_key} preserved.",
        })

    return review_items


def apply_user_decisions(review_items: list[dict], original_sections: dict = None) -> dict:
    """
    Apply user accept/reject/edit decisions.
    Returns final sections dict ready for DOCX generation.
    Merges optimized sections with ALL original sections from structured_data.
    """
    final_sections = {}
    
    # First, add ALL original sections (from structured_data)
    if original_sections:
        # Map the original sections to final format
        section_mapping = {
            "work_experience": "experience",
            "internships": "internships", 
            "technical_skills": "skills",
            "projects": "projects",
            "education": "education",
            "certifications": "certifications",
            "awards": "achievements",
            "interests": "interests",
        }
        
        for orig_key, final_key in section_mapping.items():
            if orig_key in original_sections and original_sections[orig_key]:
                content = original_sections[orig_key]
                # Convert list/dict to string if needed
                if isinstance(content, list):
                    if all(isinstance(x, dict) for x in content):
                        # Format list of dicts (like work_experience)
                        formatted = []
                        for item in content:
                            if isinstance(item, dict):
                                title = item.get("job_title", item.get("project_name", ""))
                                details = item.get("summary", "")
                                achievements = item.get("achievements", item.get("description", ""))
                                formatted.append(f"{title}\n{details}\n{achievements}")
                        content = "\n\n".join(formatted)
                    else:
                        content = "\n".join(str(x) for x in content)
                final_sections[final_key] = {
                    "label": final_key.replace("_", " ").title(),
                    "content": str(content) if content else ""
                }
    
    # Now apply user decisions (this will override originals with optimized/edited content)
    for item in review_items:
        status = item.get("status", "pending")
        section_key = item["section"]
        
        if status == "accepted":
            final_sections[section_key] = {
                "label": item["label"],
                "content": item["optimized"],
            }
        elif status == "edited":
            final_sections[section_key] = {
                "label": item["label"],
                "content": item.get("edited_content", item["optimized"]),
            }
        elif status == "rejected":
            # Keep original (already added above)
            pass
        else:
            # pending — keep original
            if section_key not in final_sections:
                final_sections[section_key] = {
                    "label": item["label"],
                    "content": item.get("original", ""),
                }
    
    return final_sections

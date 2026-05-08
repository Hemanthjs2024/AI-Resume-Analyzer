import logging

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from services.resume_parser import parse_resume, normalize_structured_data
from services.resume_optimizer import optimize_resume
from services.jd_parser import parse_jd
from services.skill_extractor import extract_user_skills
from services.gap_analyzer import analyze_gaps
from services.scoring_engine import calculate_overall_score
from services.llm_client import analyze_alignment_llm, suggest_projects_llm, _mock_suggest_projects

logger = logging.getLogger("resume-agent.analyse")
router = APIRouter()


@router.post("/analyse")
async def analyse_resume(
    resume: UploadFile = File(...),
    jd_text: str = Form(...),
):
    if not resume.filename:
        raise HTTPException(status_code=400, detail="No resume file provided")
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description text is required")

    try:
        file_bytes = await resume.read()
        logger.info("Analysing resume: %s (%d bytes)", resume.filename, len(file_bytes))

        parsed = parse_resume(file_bytes, resume.filename)
        structured_data = parsed.get("structured_data", {})
        raw_resume_text = parsed.get("raw_text", "")

        jd_data = parse_jd(jd_text)
        user_skills = extract_user_skills(parsed)
        normalized = normalize_structured_data(structured_data)
        gap_results = analyze_gaps(user_skills, jd_data.get("required_skills", []))
        ai_analysis = analyze_alignment_llm(raw_resume_text, jd_text)
        score = calculate_overall_score(
            raw_resume_text,
            normalized,
            user_skills,
            jd_data,
            ai_score=ai_analysis.get("alignment_score"),
        )
        score["ai_analysis"] = ai_analysis

        reachable_gaps = [g["skill"] for g in gap_results.get("gaps", []) if g.get("reachable")]
        all_jd_skills = jd_data.get("required_skills", [])
        suggestion_targets = reachable_gaps if reachable_gaps else all_jd_skills

        project_suggestions = suggest_projects_llm(
            user_skills, jd_text, suggestion_targets, resume_text=raw_resume_text,
        )
        if not project_suggestions:
            project_suggestions = _mock_suggest_projects(user_skills, suggestion_targets)
        for p in project_suggestions:
            p.setdefault("committed", False)

        review_items = optimize_resume(normalized, jd_data, user_skills)
        candidate_name = structured_data.get("candidate", {}).get("full_name", "Professional")

        return {
            "success": True,
            "candidate_name": candidate_name,
            "structured_data": structured_data,
            "jd_data": jd_data,
            "score": score,
            "gap_analysis": gap_results,
            "project_suggestions": project_suggestions,
            "review_items": review_items,
            "raw_text": raw_resume_text,
            "committed_projects": [],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Analyse failed for %s", resume.filename)
        raise HTTPException(status_code=500, detail=str(e))

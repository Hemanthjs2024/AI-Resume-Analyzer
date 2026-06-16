import logging
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Any

from services.resume_optimizer import apply_user_decisions
from services.resume_generator import build_docx, save_docx, convert_to_pdf

logger = logging.getLogger("resume-agent.generate")
router = APIRouter()


class GenerateRequest(BaseModel):
    review_items: list[dict[str, Any]]
    committed_projects: list[dict[str, Any]] = []
    selected_skills: list[str] = []
    candidate_name: str = "Candidate"
    template: str = "chronological_classic"
    structured_data: dict[str, Any] | None = None


@router.post("/generate")
async def generate(req: GenerateRequest):
    try:
        structured = req.structured_data or {}
        original_sections = structured.get("sections", {})
        final_sections = apply_user_decisions(req.review_items, original_sections)
        committed = [p for p in req.committed_projects if p.get("committed")]

        if req.selected_skills:
            sections = structured.setdefault("sections", {})
            skill_cats = sections.setdefault("technical_skills", [])
            existing_items = []
            for cat in skill_cats:
                existing_items.extend(cat.get("items", []))
            new_skills = [s for s in req.selected_skills if s not in existing_items]
            if new_skills:
                target_cat = next(
                    (c for c in skill_cats if c.get("category", "").lower() in ["target skills", "jd skills"]),
                    None,
                )
                if target_cat:
                    target_cat["items"].extend(new_skills)
                else:
                    skill_cats.append({"category": "Target Skills", "items": new_skills})

        docx_bytes = build_docx(final_sections, committed, req.candidate_name, req.template, structured)
        file_id = str(uuid.uuid4())[:8]
        docx_filename = f"resume_{file_id}.docx"
        docx_path = save_docx(docx_bytes, docx_filename)

        pdf_path = convert_to_pdf(docx_path)
        pdf_filename = f"resume_{file_id}.pdf" if pdf_path else None

        logger.info("Generated resume %s (pdf=%s)", docx_filename, pdf_filename)

        return {
            "success": True,
            "file_id": file_id,
            "docx_filename": docx_filename,
            "pdf_filename": pdf_filename,
            "pdf_available": pdf_path is not None,
        }

    except Exception as e:
        logger.exception("Generate failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_file(filename: str):
    from services.resume_generator import OUTPUT_DIR

    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    media_type = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if filename.endswith(".docx")
        else "application/pdf"
    )
    return FileResponse(str(file_path), media_type=media_type, filename=filename)

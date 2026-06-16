import re
import io
from pathlib import Path

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


SECTION_PATTERNS = {
    "summary": re.compile(
        r"^(summary|objective|profile|about me|professional summary|career objective|about)$", re.I
    ),
    "skills": re.compile(
        r"^(skills|technical skills|core competencies|technologies|expertise|tech stack)$", re.I
    ),
    "experience": re.compile(
        r"^(experience|work experience|employment|professional experience|work history)$", re.I
    ),
    "projects": re.compile(r"^(projects|personal projects|academic projects|portfolio)$", re.I),
    "internships": re.compile(r"^(internships|internship|intern experience|trainee|apprentice)$", re.I),
    "education": re.compile(r"^(education|academic background|qualifications|degrees|academics)$", re.I),
    "certifications": re.compile(
        r"^(certifications|certificates|licenses|credentials)$", re.I
    ),
    "achievements": re.compile(r"^(achievements|awards|honors|accomplishments)$", re.I),
    "interests": re.compile(r"^(interests|hobbies|extracurricular|activities)$", re.I),
}

DATE_RE = re.compile(
    r'\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|'
    r'jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
    r'[\s,]*\d{4}|\d{4}\s*[-–—]\s*(?:\d{4}|present|current|now|till date)',
    re.I
)
YEAR_RE = re.compile(r'\b((?:19|20)\d{2})\b')
BULLET_RE = re.compile(r'^[•\-\*–▪►→]')
EMAIL_RE = re.compile(r'[\w\.\-]+@[\w\.\-]+\.\w+')
PHONE_RE = re.compile(r'[\+]?[\d][\d\s\-\(\)\.]{8,}[\d]')
URL_RE = re.compile(r'(https?://[^\s]+|linkedin\.com/[^\s]+|github\.com/[^\s]+)', re.I)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    if not PDF_AVAILABLE:
        raise ImportError("pdfplumber not installed")
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text_parts.append(extracted)
    return "\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx not installed")
    doc = DocxDocument(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_bytes)
    else:
        return file_bytes.decode("utf-8", errors="ignore")


def detect_sections(text: str) -> dict[str, str]:
    """Split resume text into named sections using heading detection."""
    lines = text.split("\n")
    sections: dict[str, list[str]] = {"header": []}
    current_section = "header"

    for line in lines:
        stripped = line.strip()
        matched = False
        for section_name, pattern in SECTION_PATTERNS.items():
            if pattern.match(stripped) and len(stripped) < 60:
                current_section = section_name
                sections.setdefault(section_name, [])
                matched = True
                break
        if not matched:
            sections.setdefault(current_section, []).append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if v}


def _parse_dates_from_line(line: str) -> tuple[str, str]:
    """Extract start/end dates from a line. Returns (start, end)."""
    years = YEAR_RE.findall(line)
    is_present = bool(re.search(r'\b(present|current|now|till date)\b', line, re.I))
    if len(years) >= 2:
        return years[0], years[1]
    elif len(years) == 1:
        return years[0], "Present" if is_present else ""
    elif is_present:
        return "", "Present"
    return "", ""


def _clean_line(line: str) -> str:
    """Remove bullets and leading/trailing whitespace."""
    return BULLET_RE.sub("", line).strip(" •-–*▪►→\t")


def _parse_job_blocks(text: str) -> list[dict]:
    """
    Parse a block of work experience or internship text into structured job entries.
    Handles: Title / Company / Date / Bullet achievements
    """
    lines = [l for l in text.split("\n") if l.strip()]
    entries = []
    current = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        is_bullet = bool(BULLET_RE.match(stripped))
        has_date = bool(DATE_RE.search(stripped)) or bool(YEAR_RE.search(stripped))
        is_short = len(stripped) < 80

        if is_bullet:
            # Achievement bullet — attach to current entry
            if current is None:
                current = {"job_title": "", "employer": "", "start_date": "", "end_date": "", "summary": "", "achievements": []}
            current["achievements"].append(_clean_line(stripped))

        elif has_date and is_short:
            # Line has a date — it could be "Job Title     2020 – 2022" or "Company | City   Jan 2021 – Present"
            start, end = _parse_dates_from_line(stripped)
            # Remove date portion to get the label
            label = re.sub(
                r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|'
                r'jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
                r'[\s,]*\d{4}|\d{4}|present|current|now|till date|[-–—|,]', "", stripped, flags=re.I
            ).strip()

            if current is None:
                # First line with date — treat as job title + date
                current = {
                    "job_title": label,
                    "employer": "",
                    "start_date": start,
                    "end_date": end,
                    "summary": "",
                    "achievements": []
                }
            elif not current.get("start_date"):
                # We have a job title already, this is the company/date line
                if label and not current.get("employer"):
                    current["employer"] = label
                current["start_date"] = start
                current["end_date"] = end
            else:
                # New entry — save current and start new
                if current.get("job_title"):
                    entries.append(current)
                current = {
                    "job_title": label,
                    "employer": "",
                    "start_date": start,
                    "end_date": end,
                    "summary": "",
                    "achievements": []
                }
        else:
            # Plain text line — job title or company name
            if current is None:
                current = {
                    "job_title": stripped,
                    "employer": "",
                    "start_date": "",
                    "end_date": "",
                    "summary": "",
                    "achievements": []
                }
            elif not current.get("employer") and current.get("job_title") and not current.get("start_date"):
                # Second plain line after title — company name
                current["employer"] = stripped
            elif current.get("employer") or current.get("start_date"):
                # After company/date — could be a summary sentence
                if not current.get("summary") and not is_bullet:
                    current["summary"] = stripped
                else:
                    # New job title — save and start fresh
                    if current.get("job_title"):
                        entries.append(current)
                    current = {
                        "job_title": stripped,
                        "employer": "",
                        "start_date": "",
                        "end_date": "",
                        "summary": "",
                        "achievements": []
                    }

    if current and current.get("job_title"):
        entries.append(current)

    return entries


def _parse_education_blocks(text: str) -> list[dict]:
    """Parse education section into structured entries."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    entries = []
    current = None

    for line in lines:
        is_bullet = bool(BULLET_RE.match(line))
        has_date = bool(DATE_RE.search(line)) or bool(YEAR_RE.search(line))
        cgpa_match = re.search(r'(cgpa|gpa|percentage|score|grade)[:\s]+([0-9\.]+)', line, re.I)
        is_short = len(line) < 80

        if is_bullet:
            continue  # Skip bullets in education

        if cgpa_match:
            if current:
                current["cgpa"] = cgpa_match.group(2)
            continue

        if has_date and is_short:
            start, end = _parse_dates_from_line(line)
            label = re.sub(
                r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|'
                r'jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
                r'[\s,]*\d{4}|\d{4}|present|current|now|till date|[-–—|,]', "", line, flags=re.I
            ).strip()

            if current and not current.get("start_date"):
                current["start_date"] = start
                current["end_date"] = end
                if label and not current.get("institution"):
                    current["institution"] = label
            elif current:
                entries.append(current)
                current = {
                    "institution": label or line,
                    "degree": "",
                    "start_date": start,
                    "end_date": end,
                    "cgpa": ""
                }
            else:
                current = {
                    "institution": label or line,
                    "degree": "",
                    "start_date": start,
                    "end_date": end,
                    "cgpa": ""
                }
        else:
            # Degree or institution line
            if current is None:
                current = {
                    "institution": line,
                    "degree": "",
                    "start_date": "",
                    "end_date": "",
                    "cgpa": ""
                }
            elif not current.get("degree") and current.get("institution"):
                # Check if this could be a degree (often contains "B.", "M.", "Bachelor", "Master", "B.Tech", etc.)
                degree_keywords = re.search(r'\b(b\.?e|b\.?tech|m\.?tech|b\.?sc|m\.?sc|bca|mca|bachelor|master|phd|diploma|b\.?com|mba)\b', line, re.I)
                if degree_keywords or len(line) < len(current["institution"]):
                    # Swap: this line is degree, previous was institution
                    current["degree"] = line
                else:
                    # This is a new institution — save current
                    entries.append(current)
                    current = {
                        "institution": line,
                        "degree": "",
                        "start_date": "",
                        "end_date": "",
                        "cgpa": ""
                    }
            else:
                entries.append(current)
                current = {
                    "institution": line,
                    "degree": "",
                    "start_date": "",
                    "end_date": "",
                    "cgpa": ""
                }

    if current:
        entries.append(current)

    return entries


def _parse_projects(text: str) -> list[dict]:
    """Parse projects section into structured entries."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    entries = []
    current = None

    for line in lines:
        is_bullet = bool(BULLET_RE.match(line))

        if is_bullet:
            if current:
                clean = _clean_line(line)
                if not current["description"]:
                    current["description"] = clean
                else:
                    current["description"] += " " + clean
            continue

        # Check for tech stack indicators
        tech_match = re.search(r'(?:tech(?:nologies)?|stack|tools?|built with)[:\s]+(.+)', line, re.I)
        if tech_match and current:
            techs = [t.strip() for t in re.split(r'[,|]', tech_match.group(1)) if t.strip()]
            current["technologies"].extend(techs)
            continue

        # Parenthetical tech list e.g. "Project Name (React, Node.js)"
        paren_match = re.match(r'^(.+?)\s*\(([^)]+)\)$', line)
        if paren_match:
            name = paren_match.group(1).strip()
            techs = [t.strip() for t in paren_match.group(2).split(",") if t.strip()]
            if current:
                entries.append(current)
            current = {
                "project_name": name,
                "description": "",
                "technologies": techs
            }
            continue

        # New project title
        if current:
            entries.append(current)
        current = {
            "project_name": line,
            "description": "",
            "technologies": []
        }

    if current:
        entries.append(current)

    return entries


def _parse_skills(text: str) -> list[dict]:
    """Parse skills section into categorized lists."""
    result = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    for line in lines:
        # Check for "Category: skill1, skill2" pattern
        colon_match = re.match(r'^(.{2,40}):\s*(.+)$', line)
        if colon_match:
            category = colon_match.group(1).strip()
            items_str = colon_match.group(2).strip()
            items = [s.strip() for s in re.split(r'[,|•]', items_str) if s.strip()]
            if items:
                result.append({"category": category, "items": items})
        else:
            # Flat list — split by comma or bullet
            items = [_clean_line(s) for s in re.split(r'[,|•\n]', line) if s.strip()]
            if items:
                if result and result[-1]["category"] == "Technical Skills":
                    result[-1]["items"].extend(items)
                else:
                    result.append({"category": "Technical Skills", "items": items})

    return result


def extract_structured_data_rule_based(raw_text: str, sections: dict[str, str]) -> dict:
    """
    Robust rule-based extractor. Produces pin-to-pin accurate structured data
    from the raw resume text and pre-detected sections.
    """
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

    # ── Candidate Info ──────────────────────────────────────────────────────
    email = (EMAIL_RE.search(raw_text) or object())
    phone = (PHONE_RE.search(raw_text) or object())
    linkedin = ""
    github = ""
    for m in URL_RE.finditer(raw_text):
        url = m.group(0)
        if "linkedin" in url.lower():
            linkedin = url
        elif "github" in url.lower():
            github = url

    # Name: first non-empty non-contact line
    name = "Candidate"
    for l in lines[:5]:
        if not EMAIL_RE.search(l) and not PHONE_RE.search(l) and not URL_RE.search(l):
            name = l
            break

    # Location: look for "City, State" or "City, Country" pattern near top
    location = {"city": "", "state": ""}
    loc_match = re.search(r'\b([A-Z][a-z]+),\s*([A-Z][a-z]+|[A-Z]{2})\b', "\n".join(lines[:10]))
    if loc_match:
        location = {"city": loc_match.group(1), "state": loc_match.group(2)}

    summary_text = sections.get("summary", "")

    candidate = {
        "full_name": name,
        "email": email.group(0) if hasattr(email, "group") else "",
        "phone": phone.group(0).strip() if hasattr(phone, "group") else "",
        "location": location,
        "linkedin_url": linkedin,
        "github_url": github,
        "summary": summary_text,
    }

    # ── Sections ────────────────────────────────────────────────────────────
    work_exp = _parse_job_blocks(sections.get("experience", ""))
    internships = _parse_job_blocks(sections.get("internships", ""))
    education = _parse_education_blocks(sections.get("education", ""))
    projects = _parse_projects(sections.get("projects", ""))
    skills = _parse_skills(sections.get("skills", ""))

    # Certifications — simple line-by-line
    certs = []
    for line in sections.get("certifications", "").split("\n"):
        line = _clean_line(line)
        if line:
            certs.append({"name": line, "issuer": "", "date": ""})

    # Awards
    awards = []
    for line in sections.get("achievements", "").split("\n"):
        line = _clean_line(line)
        if line:
            awards.append({"title": line, "issuer": "", "date": ""})

    # Interests
    raw_interests = sections.get("interests", "")
    interests = [_clean_line(s) for s in re.split(r'[,\n•]', raw_interests) if _clean_line(s)]

    return {
        "candidate": candidate,
        "sections": {
            "work_experience": work_exp,
            "internships": internships,
            "technical_skills": skills,
            "education": education,
            "projects": projects,
            "certifications": certs,
            "awards": awards,
            "interests": interests,
        }
    }


from . import llm_client


def parse_resume(file_bytes: bytes, filename: str) -> dict:
    """Full resume parse: extract text → detect sections → rule-based extraction → optionally AI-enhance."""
    raw_text = extract_text(file_bytes, filename)
    sections = detect_sections(raw_text)

    # Always run rule-based first — it's reliable
    rb_data = extract_structured_data_rule_based(raw_text, sections)

    # Try AI structuring — only use if real LLM is available
    if llm_client.USE_REAL_LLM:
        ai_data = llm_client.structure_resume_llm(raw_text)
        ai_name = ai_data.get("candidate", {}).get("full_name", "")
        # Only use AI data if it actually extracted a real name (not a mock placeholder)
        if ai_name and ai_name not in ["John Doe", "Candidate Name", "Candidate", ""]:
            structured_data = ai_data
        else:
            structured_data = rb_data
    else:
        structured_data = rb_data

    return {
        "raw_text": raw_text,
        "sections": sections,
        "structured_data": structured_data,
        "filename": filename,
    }


def normalize_structured_data(structured_data: dict) -> dict[str, str]:
    """
    Converts structured JSON into flat {section: string} for the optimizer.
    """
    sections = structured_data.get("sections", {})
    candidate = structured_data.get("candidate", {})

    normalized = {}

    # Summary
    normalized["summary"] = candidate.get("summary", "")

    # Skills
    skills_list = sections.get("technical_skills", [])
    skills_text = []
    if isinstance(skills_list, list):
        for cat in skills_list:
            if isinstance(cat, dict):
                label = cat.get("category", "")
                items = cat.get("items", [])
                if label and items:
                    skills_text.append(f"{label}: {', '.join(items)}")
                elif items:
                    skills_text.append(", ".join(items))
            elif isinstance(cat, str):
                skills_text.append(cat)
    normalized["skills"] = "\n".join(skills_text)

    # Experience
    def _format_jobs(job_list):
        blocks = []
        for job in (job_list or []):
            if not isinstance(job, dict):
                continue
            title = job.get("job_title", "")
            employer = job.get("employer", "")
            start = job.get("start_date", "")
            end = job.get("end_date", "")
            summary = job.get("summary", "")
            achievements = job.get("achievements", [])
            date_str = f"{start} – {end}".strip(" –") if (start or end) else ""
            header = f"{title} | {employer}" if employer else title
            if date_str:
                header += f" | {date_str}"
            block = header
            if summary:
                block += f"\n{summary}"
            for ach in (achievements or []):
                block += f"\n• {ach}"
            blocks.append(block)
        return "\n\n".join(blocks)

    normalized["experience"] = _format_jobs(sections.get("work_experience", []))
    normalized["internships"] = _format_jobs(sections.get("internships", []))

    # Projects
    proj_list = sections.get("projects", [])
    proj_text = []
    for proj in (proj_list or []):
        if not isinstance(proj, dict):
            continue
        name = proj.get("project_name", "")
        desc = proj.get("description", "")
        tech = proj.get("technologies", [])
        block = name
        if tech:
            block += f" ({', '.join(tech)})"
        if desc:
            block += f"\n{desc}"
        proj_text.append(block)
    normalized["projects"] = "\n\n".join(proj_text)

    # Education
    edu_list = sections.get("education", [])
    edu_text = []
    for edu in (edu_list or []):
        if not isinstance(edu, dict):
            continue
        deg = edu.get("degree", "")
        inst = edu.get("institution", "")
        cgpa = edu.get("cgpa", "")
        start = edu.get("start_date", "")
        end = edu.get("end_date", "")
        date_str = f"{start} – {end}".strip(" –") if (start or end) else ""
        parts = [p for p in [deg, inst] if p]
        line = " | ".join(parts)
        if date_str:
            line += f" | {date_str}"
        if cgpa:
            line += f" | CGPA: {cgpa}"
        edu_text.append(line)
    normalized["education"] = "\n".join(edu_text)

    # Interests
    interests = sections.get("interests", [])
    if isinstance(interests, list):
        normalized["interests"] = ", ".join(interests)
    else:
        normalized["interests"] = str(interests)

    # Certifications
    cert_list = sections.get("certifications", [])
    certs = [c.get("name", "") for c in cert_list if isinstance(c, dict) and c.get("name")]
    normalized["certifications"] = "\n".join(certs)

    return normalized

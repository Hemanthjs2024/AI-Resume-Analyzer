import re
from services.skill_graph import get_all_skills, normalize_skill

# Common JD patterns
_REQ_PATTERNS = [
    re.compile(r"required?\s*skills?[:\-]?\s*(.*)", re.I),
    re.compile(r"must\s+have[:\-]?\s*(.*)", re.I),
    re.compile(r"you\s+(?:should|must|will)\s+(?:have|know|be)[:\-]?\s*(.*)", re.I),
    re.compile(r"qualifications?[:\-]?\s*(.*)", re.I),
    re.compile(r"requirements?[:\-]?\s*(.*)", re.I),
    re.compile(r"experience\s+(?:with|in)[:\-]?\s*(.*)", re.I),
]

_NICE_PATTERNS = [
    re.compile(r"nice\s+to\s+have[:\-]?\s*(.*)", re.I),
    re.compile(r"preferred?[:\-]?\s*(.*)", re.I),
    re.compile(r"bonus[:\-]?\s*(.*)", re.I),
]

RESPONSIBILITY_KEYWORDS = [
    "design", "develop", "implement", "maintain", "collaborate", "lead",
    "manage", "build", "create", "optimize", "support", "deploy", "architect",
    "integrate", "monitor", "analyze", "test", "review", "mentor"
]


def extract_skills_from_text(text: str) -> list[str]:
    """Match text against skill graph vocabulary."""
    all_skills = get_all_skills()
    found = set()
    text_lower = text.lower()
    for skill in all_skills:
        # Word-boundary match
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)
    return sorted(found)


def extract_responsibilities(text: str) -> list[str]:
    lines = text.split("\n")
    responsibilities = []
    for line in lines:
        stripped = line.strip().lstrip("•-–*").strip()
        if any(kw in stripped.lower() for kw in RESPONSIBILITY_KEYWORDS) and len(stripped) > 20:
            responsibilities.append(stripped)
    return responsibilities[:10]


def parse_jd(jd_text: str) -> dict:
    """Parse job description into structured output using AI."""
    from .llm_client import parse_jd_llm
    
    # 1. AI Parsing
    ai_data = parse_jd_llm(jd_text)
    
    # 2. Rule-based fallback/augmentation
    required_skills_rb = extract_skills_from_text(jd_text)
    responsibilities_rb = extract_responsibilities(jd_text)
    
    # Merge skills (AI + local graph matching)
    all_req_skills = list(set(ai_data.get("required_skills", []) + required_skills_rb))
    
    # Ensure education_requirements exists
    edu = ai_data.get("education_requirements", {
        "degree": "Not specified",
        "major": [],
        "min_years_experience": 0
    })

    return {
        "job_title": ai_data.get("job_title", "Software Engineer"),
        "required_skills": all_req_skills,
        "nice_to_have_skills": ai_data.get("preferred_skills", []),
        "latent_skills": ai_data.get("latent_skills", []),
        "education_requirements": edu,
        "responsibilities": ai_data.get("responsibilities", responsibilities_rb),
        "raw_text": jd_text,
    }

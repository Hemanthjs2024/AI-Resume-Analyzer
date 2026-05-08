import re
from services.skill_graph import get_all_skills, normalize_skill


def extract_skills_from_text(text: str) -> list[str]:
    """Extract skills from any text block by matching against skill graph vocabulary."""
    all_skills = get_all_skills()
    found = set()
    text_lower = text.lower()
    for skill in all_skills:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            canonical = normalize_skill(skill)
            if canonical:
                found.add(canonical)
    return sorted(found)


def extract_user_skills(resume_data: dict) -> list[str]:
    """Extract user skills from parsed resume sections."""
    sections = resume_data.get("sections", {})
    raw_text = resume_data.get("raw_text", "")

    # Skills section is highest priority
    skills_text = sections.get("skills", "")
    experience_text = sections.get("experience", "")
    projects_text = sections.get("projects", "")

    combined = f"{skills_text}\n{experience_text}\n{projects_text}"
    found = set(extract_skills_from_text(combined))

    # Also scan full text for any missed ones
    all_found = set(extract_skills_from_text(raw_text))
    found.update(all_found)

    return sorted(found)


def categorize_skills(skills: list[str]) -> dict[str, list[str]]:
    """Categorize skills by domain."""
    categories = {
        "programming_languages": ["Python", "JavaScript", "TypeScript", "Java", "C++", "Rust", "Go", "Kotlin", "Swift", "R"],
        "frontend": ["React", "Vue.js", "Angular", "Next.js", "HTML", "CSS", "SASS", "Tailwind CSS"],
        "backend": ["Django", "Flask", "FastAPI", "Node.js", "Express.js", "Spring Boot"],
        "data_ml": ["Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "NLP", "Machine Learning", "Deep Learning"],
        "databases": ["SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis"],
        "devops_cloud": ["Docker", "Kubernetes", "AWS", "GCP", "Azure", "CI/CD", "GitHub Actions"],
        "tools": ["Git", "GitHub", "Postman", "Figma", "Linux"],
        "testing": ["Selenium", "Playwright", "Jest", "Unit Testing"],
        "mobile": ["Android", "iOS Development", "React Native", "Flutter"],
    }
    result = {}
    for cat, cat_skills in categories.items():
        matched = [s for s in skills if s in cat_skills]
        if matched:
            result[cat] = matched
    return result

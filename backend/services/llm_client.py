import json
import logging
import os
import re
import random
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

logger = logging.getLogger("resume-agent.llm")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
USE_REAL_LLM = bool(GOOGLE_API_KEY and GOOGLE_API_KEY not in ("your-key-here", "your-google-api-key-here"))

PROMPTS = {
    "optimize_summary": """
You are an expert resume writer. Rewrite the following resume summary to be:
- Professional and compelling
- 3-4 sentences max
- ATS-friendly with relevant keywords
- Starting with a strong opening statement

User's current summary:
{current_summary}

Target Job Description keywords:
{jd_keywords}

Return ONLY the improved summary text. No explanations.
""",
    "optimize_experience": """
You are an expert resume writer. Improve the following experience section:
- Start each bullet with a strong action verb
- Add quantifiable metrics where possible (estimate if needed — but only realistic ones)
- Remove vague language
- Keep it ATS-optimized for: {job_title}

Current experience:
{current_experience}

Return ONLY the improved experience lines as bullet points. No explanations.
""",
    "optimize_skills": """
Rewrite the following skills section to be ATS-optimized for the given job.
Include ALL existing skills plus suggest adding: {missing_skills}
Only include skills the user actually has listed below.

Current skills:
{current_skills}

Return ONLY the skills list, comma-separated or as bullet points. No explanations.
""",
    "chat_refine": """
You are an AI career assistant helping a user refine their resume.
Resume context:
{resume_context}

JD context:
{jd_context}

User's request: {user_message}

Provide a specific, actionable response. Keep it concise (max 3 paragraphs).
If they want a section rewritten, provide the rewritten version.
""",
    "suggest_projects": """
You are an expert career advisor. Suggest 3 HIGH-VALUE strategic projects to bridge the user's skill gaps for the target job.

User Context:
Current Resume: {resume_text}
Current Skills: {user_skills}
Target Job Description: {jd_text}
Skill Gaps to Bridge: {gaps}

Rules for each project:
- Each project MUST have EXACTLY 3 bullet points (field: "bullets").
- Each bullet point must be between 15 and 22 words.
- The 3 bullets combined MUST be between 50 and 62 words in total.
- Bullet 1: What was built and what technology was used.
- Bullet 2: Key technical challenge solved or feature implemented.
- Bullet 3: Outcome or impact (quantified where possible).
- Include: title, tech_stack (list), estimated_time, difficulty, target_skill, strategic_weight (0-100).
- The "description" field should be a concise 1-sentence summary (max 15 words).

Return ONLY a JSON list. No extra text.
Format:
[
  {{
    "title": "...",
    "bullets": [
      "Built a ... using ... to ...",
      "Implemented ... that ...",
      "Reduced/Improved ... by ... resulting in ..."
    ],
    "description": "...",
    "tech_stack": ["...", "..."],
    "estimated_time": "3-4 weeks",
    "difficulty": "Intermediate",
    "target_skill": "...",
    "strategic_weight": 90
  }}
]
""",
    "structure_resume": """
You are an expert resume parser. Convert the following raw resume text into a structured JSON object according to the schema provided.

Schema Requirements:
- Extract full name, email, phone, location, and social links for the candidate.
- Organize work experience into a list of objects (job_title, employer, start_date, end_date, summary, achievements list).
- Separate internships from full-time experience if possible, otherwise group in work experience.
- Organize education into a list of objects (institution, degree, start_date, end_date, cgpa).
- Group technical skills by category if possible.
- Extract certifications, awards, projects, and interests into their respective lists.

Raw Resume Text:
{raw_text}

Return ONLY the JSON object. No explanations.
Schema:
{{
  "candidate": {{ "full_name": "", "email": "", "phone": "", "location": {{ "city": "", "state": "" }}, "linkedin_url": "", "github_url": "", "summary": "" }},
  "sections": {{
    "work_experience": [ {{ "job_title": "", "employer": "", "start_date": "", "end_date": "", "summary": "", "achievements": [] }} ],
    "internships": [ {{ "job_title": "", "employer": "", "start_date": "", "end_date": "", "summary": "", "achievements": [] }} ],
    "technical_skills": [ {{ "category": "", "items": [] }} ],
    "education": [ {{ "institution": "", "degree": "", "start_date": "", "end_date": "", "cgpa": "" }} ],
    "projects": [ {{ "project_name": "", "description": "", "technologies": [] }} ],
    "certifications": [ {{ "name": "", "issuer": "", "date": "" }} ],
    "awards": [ {{ "title": "", "issuer": "", "date": "" }} ],
    "interests": []
  }}
}}
""",
    "analyze_alignment": """
You are an expert technical recruiter and career coach. Your task is to analyze the alignment between a candidate's resume and a specific job description.

Input:
Resume Content: {resume_text}
Job Description: {jd_text}

Analysis Requirements:
1. Overall Alignment Score: A score from 0-100 reflecting how well the candidate matches the role requirements.
2. Skill Match Analysis: Evaluate technical skills. Identify strong matches and critical gaps.
3. Project Relevance: How well do the candidate's listed projects demonstrate the skills required for this JD?
4. Education & Background Fit: Does their background align with the role seniority and domain?
5. Strategic Feedback: What is the most important thing they should add or change to improve their chances?

Return ONLY a JSON object. No intro/outro text.
Format:
{{
  "alignment_score": 85,
  "grade": "A",
  "reasoning": "...",
  "dimension_scores": {{
    "skills": 90,
    "projects": 80,
    "education": 85
  }},
  "feedback": {{
    "strengths": ["...", "..."],
    "gaps": ["...", "..."],
    "strategic_advice": "..."
  }}
}}
""",
    "parse_jd": """
You are an expert technical recruiter. Parse the following Job Description (JD) into a structured format.

If skills are not explicitly listed, use your industry knowledge to infer the most critical skills required for the given Job Title.
Identify education requirements specifically (e.g., "Bachelor's in Computer Science").

Input JD Text:
{jd_text}

Return ONLY a JSON object. No intro/outro text.
Format:
{{
  "job_title": "...",
  "required_skills": ["...", "..."],
  "preferred_skills": ["...", "..."],
  "latent_skills": ["...", "..."],
  "education_requirements": {{
    "degree": "...",
    "major": ["...", "..."],
    "min_years_experience": 0
  }},
  "responsibilities": ["...", "..."]
}}
""",
}


def _mock_optimize_summary(current_summary: str, jd_keywords: list[str]) -> str:
    kw_str = ", ".join(jd_keywords[:4]) if jd_keywords else "software development"
    opening_hooks = [
        "Results-driven software professional",
        "Passionate and detail-oriented developer",
        "Dedicated technology enthusiast",
        "Motivated software engineer",
    ]
    hook = random.choice(opening_hooks)
    last_kw = jd_keywords[-1] if jd_keywords else "modern technologies"
    return (
        f"{hook} with a strong foundation in {kw_str}. "
        f"Experienced in building scalable, maintainable solutions and collaborating effectively within agile teams. "
        f"Actively expanding expertise in {last_kw} "
        f"to deliver high-impact results. "
        f"Seeking a role where technical skills and a growth mindset can drive meaningful outcomes."
    )


def _mock_optimize_experience(current_experience: str, job_title: str) -> str:
    lines = [l.strip().lstrip("•-–*").strip() for l in current_experience.split("\n") if l.strip()]
    strong_verbs = ["Developed", "Built", "Implemented", "Optimized", "Collaborated on", "Maintained", "Designed"]
    improved = []
    for i, line in enumerate(lines[:6]):
        if line:
            verb = strong_verbs[i % len(strong_verbs)]
            starts_with_verb = any(line.lower().startswith(v.lower()) for v in strong_verbs)
            if starts_with_verb:
                improved.append(f"• {line}")
            else:
                improved.append(f"• {verb} {line[0].lower()}{line[1:]}")
    if not improved:
        improved = [f"• Contributed to {job_title} responsibilities and team objectives."]
    return "\n".join(improved)


def _mock_optimize_skills(current_skills: str, missing_skills: list[str]) -> str:
    existing = [s.strip() for s in re.split(r'[,\n•\-]', current_skills) if s.strip()]
    suggestions = [f"{s} (learning)" for s in missing_skills[:3]]
    return ", ".join(existing + suggestions)


def _mock_chat_response(user_message: str, resume_context: str, jd_context: str) -> dict:
    msg_lower = user_message.lower()
    if "summary" in msg_lower or "profile" in msg_lower:
        return {
            "response": "I've revised your summary to be more impactful and ATS-friendly.",
            "updated_section": "summary",
            "updated_content": _mock_optimize_summary(resume_context, jd_context.split()[:5]),
        }
    elif "keyword" in msg_lower or "skill" in msg_lower:
        return {
            "response": "I've enhanced the skills section to include more relevant keywords from the JD.",
            "updated_section": "skills",
            "updated_content": resume_context[:300] + "\n• Docker, CI/CD, REST API (from JD analysis)",
        }
    elif "bullet" in msg_lower or "experience" in msg_lower:
        return {
            "response": "I've rewritten your experience bullets with stronger action verbs and metrics.",
            "updated_section": "experience",
            "updated_content": _mock_optimize_experience(resume_context, "Software Engineer"),
        }
    else:
        return {
            "response": (
                "Great question! Here are my suggestions based on your resume and the target JD:\n\n"
                "1. Add more quantified achievements (e.g., 'Reduced build time by 30%')\n"
                "2. Include keywords from the JD in your skills and summary sections\n"
                "3. Use strong action verbs at the start of each bullet point\n\n"
                "Would you like me to rewrite any specific section?"
            ),
            "updated_section": None,
            "updated_content": None,
        }


def _mock_suggest_projects(user_skills: list[str], gaps: list[str]) -> list[dict]:
    targets = (gaps[:3] if gaps else user_skills[:3]) or ["Software Engineering", "Data Pipelines", "Cloud APIs"]
    while len(targets) < 3:
        targets.append(["REST APIs", "System Design", "Automation"][len(targets) % 3])

    MOCK_TEMPLATES = [
        {
            "title_tmpl": "{skill} Analytics Platform",
            "bullets_tmpl": [
                "Built a scalable analytics platform integrating {user_skill} and {skill} to process real-time event streams for business intelligence.",
                "Designed and implemented data ingestion pipelines with automated validation, reducing data processing errors by thirty-five percent.",
                "Delivered an interactive dashboard increasing stakeholder decision-making speed by forty percent and reducing manual reporting overhead.",
            ],
            "desc_tmpl": "End-to-end analytics solution leveraging {skill} for real-time insights.",
        },
        {
            "title_tmpl": "{skill} Automation Engine",
            "bullets_tmpl": [
                "Developed a robust automation engine using {user_skill} and {skill} to eliminate repetitive manual workflows across enterprise teams.",
                "Implemented intelligent scheduling and retry logic, achieving ninety-nine percent task success rate under high-load conditions.",
                "Reduced manual intervention by sixty percent and saved twelve hours of engineering time weekly across the organization.",
            ],
            "desc_tmpl": "Intelligent automation solution built with {skill} for enterprise workflows.",
        },
        {
            "title_tmpl": "{skill} Microservice API",
            "bullets_tmpl": [
                "Architected and built a production-ready microservice API using {user_skill} and {skill} with JWT authentication and rate limiting.",
                "Implemented comprehensive test coverage and CI/CD pipeline, achieving ninety-five percent code coverage with automated deployment.",
                "Achieved sub-fifty millisecond response time serving ten thousand requests per minute in load testing environments.",
            ],
            "desc_tmpl": "Production-grade REST microservice demonstrating {skill} and API design skills.",
        },
    ]

    projects = []
    for i, target_skill in enumerate(targets[:3]):
        tmpl = MOCK_TEMPLATES[i % len(MOCK_TEMPLATES)]
        user_skill = user_skills[0] if user_skills else "Python"
        projects.append({
            "title": tmpl["title_tmpl"].format(skill=target_skill),
            "description": tmpl["desc_tmpl"].format(skill=target_skill),
            "bullets": [b.format(skill=target_skill, user_skill=user_skill) for b in tmpl["bullets_tmpl"]],
            "tech_stack": list(dict.fromkeys([user_skill, target_skill] + (user_skills[1:3] if len(user_skills) > 1 else []))),
            "estimated_time": ["3-4 weeks", "2-3 weeks", "4-5 weeks"][i % 3],
            "difficulty": ["Intermediate", "Beginner", "Advanced"][i % 3],
            "target_skill": target_skill,
            "strategic_weight": [90, 85, 80][i % 3],
            "committed": False,
        })
    return projects


def _mock_analyze_alignment(resume_text: str, jd_text: str) -> dict:
    return {
        "alignment_score": 65,
        "grade": "C",
        "reasoning": "The candidate has solid foundational skills but lacks direct experience in the specific tech stack requested in the JD.",
        "dimension_scores": {"skills": 60, "projects": 70, "education": 80},
        "feedback": {
            "strengths": ["Solid educational background", "Relevant foundational skills"],
            "gaps": ["Missing cloud experience", "No production-level React projects"],
            "strategic_advice": "Focus on building a full-stack project using the requested tech stack to bridge the gap.",
        },
    }


def _mock_parse_jd(jd_text: str) -> dict:
    return {
        "job_title": "Full Stack Developer",
        "required_skills": ["React", "Node.js", "JavaScript"],
        "preferred_skills": ["TypeScript", "Docker"],
        "latent_skills": ["Git", "REST APIs", "Unit Testing"],
        "education_requirements": {
            "degree": "Bachelor's",
            "major": ["Computer Science", "Software Engineering"],
            "min_years_experience": 2,
        },
        "responsibilities": ["Develop new features", "Maintain existing code"],
    }


def _mock_structure_resume(raw_text: str) -> dict:
    return {
        "candidate": {
            "full_name": "", "email": "", "phone": "",
            "location": {"city": "", "state": ""},
            "linkedin_url": "", "github_url": "", "summary": "",
        },
        "sections": {
            "work_experience": [], "internships": [], "technical_skills": [],
            "education": [], "projects": [], "certifications": [], "awards": [], "interests": [],
        },
    }


def _extract_json(raw: str, default: str = '{}') -> str:
    if not raw or not isinstance(raw, str):
        return default
    clean = re.sub(r'```(?:json)?', '', raw).strip()
    clean = clean.strip('`').strip()
    for start_char, end_char in [('[', ']'), ('{', '}')]:
        start = clean.find(start_char)
        end = clean.rfind(end_char)
        if start != -1 and end != -1 and end > start:
            return clean[start:end + 1]
    return default


def _call_llm(prompt: str) -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error("LLM call failed: %s", e)
        return ""


def optimize_summary(current_summary: str, jd_keywords: list[str]) -> str:
    if USE_REAL_LLM:
        return _call_llm(PROMPTS["optimize_summary"].format(
            current_summary=current_summary, jd_keywords=", ".join(jd_keywords),
        ))
    return _mock_optimize_summary(current_summary, jd_keywords)


def optimize_experience(current_experience: str, job_title: str) -> str:
    if USE_REAL_LLM:
        return _call_llm(PROMPTS["optimize_experience"].format(
            current_experience=current_experience, job_title=job_title,
        ))
    return _mock_optimize_experience(current_experience, job_title)


def optimize_skills(current_skills: str, missing_skills: list[str]) -> str:
    if USE_REAL_LLM:
        return _call_llm(PROMPTS["optimize_skills"].format(
            current_skills=current_skills, missing_skills=", ".join(missing_skills[:5]),
        ))
    return _mock_optimize_skills(current_skills, missing_skills)


def chat_with_resume(user_message: str, resume_context: str, jd_context: str) -> dict:
    if USE_REAL_LLM:
        raw = _call_llm(PROMPTS["chat_refine"].format(
            resume_context=resume_context[:1000], jd_context=jd_context[:500],
            user_message=user_message,
        ))
        return {"response": raw, "updated_section": None, "updated_content": None}
    return _mock_chat_response(user_message, resume_context, jd_context)


def suggest_projects_llm(
    user_skills: list[str], jd_text: str, gaps: list[str], resume_text: str = "",
) -> list[dict]:
    if not USE_REAL_LLM:
        return _mock_suggest_projects(user_skills, gaps)
    raw = _call_llm(PROMPTS["suggest_projects"].format(
        resume_text=resume_text[:2000], user_skills=", ".join(user_skills),
        jd_text=jd_text[:1000], gaps=", ".join(gaps),
    ))
    try:
        projs = json.loads(_extract_json(raw, default='[]'))
        if not projs:
            return _mock_suggest_projects(user_skills, gaps)
        for p in projs:
            if "bullets" not in p and "description" in p:
                p["bullets"] = [p["description"]]
        return projs
    except Exception as e:
        logger.warning("Failed to parse LLM projects: %s", e)
        return _mock_suggest_projects(user_skills, gaps)


def structure_resume_llm(raw_text: str) -> dict:
    if not USE_REAL_LLM:
        return _mock_structure_resume(raw_text)
    raw = _call_llm(PROMPTS["structure_resume"].format(raw_text=raw_text[:3000]))
    try:
        return json.loads(_extract_json(raw, default='{}'))
    except Exception as e:
        logger.warning("Failed to parse structured resume: %s", e)
        return _mock_structure_resume(raw_text)


def analyze_alignment_llm(resume_text: str, jd_text: str) -> dict:
    if not USE_REAL_LLM:
        return _mock_analyze_alignment(resume_text, jd_text)
    raw = _call_llm(PROMPTS["analyze_alignment"].format(
        resume_text=resume_text[:3000], jd_text=jd_text[:1500],
    ))
    try:
        result = json.loads(_extract_json(raw, default='{}'))
        if not result or not result.get("reasoning"):
            return _mock_analyze_alignment(resume_text, jd_text)
        return result
    except Exception as e:
        logger.warning("Failed to parse alignment analysis: %s", e)
        return _mock_analyze_alignment(resume_text, jd_text)


def parse_jd_llm(jd_text: str) -> dict:
    if not USE_REAL_LLM:
        return _mock_parse_jd(jd_text)
    raw = _call_llm(PROMPTS["parse_jd"].format(jd_text=jd_text[:2000]))
    try:
        return json.loads(_extract_json(raw, default='{}'))
    except Exception as e:
        logger.warning("Failed to parse JD: %s", e)
        return _mock_parse_jd(jd_text)

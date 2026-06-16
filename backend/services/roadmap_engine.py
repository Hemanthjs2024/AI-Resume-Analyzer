"""
Roadmap Engine
Generates personalized weekly career roadmaps based on skill gaps and committed projects.
"""

RESOURCES_DB = {
    "Python": [
        {"title": "Python Official Tutorial", "url": "https://docs.python.org/3/tutorial/", "type": "docs"},
        {"title": "Automate the Boring Stuff", "url": "https://automatetheboringstuff.com/", "type": "book"},
        {"title": "Real Python Tutorials", "url": "https://realpython.com/", "type": "website"},
    ],
    "React": [
        {"title": "React Official Docs", "url": "https://react.dev/", "type": "docs"},
        {"title": "Scrimba React Course", "url": "https://scrimba.com/learn/learnreact", "type": "course"},
        {"title": "Full Stack Open", "url": "https://fullstackopen.com/", "type": "course"},
    ],
    "Selenium": [
        {"title": "Selenium Docs", "url": "https://www.selenium.dev/documentation/", "type": "docs"},
        {"title": "TestAutomationU - Selenium", "url": "https://testautomationu.applitools.com/", "type": "course"},
        {"title": "Udemy - Selenium WebDriver", "url": "https://www.udemy.com/course/selenium-real-time-examplesinterview-questions/", "type": "course"},
    ],
    "Django": [
        {"title": "Django Official Docs", "url": "https://docs.djangoproject.com/", "type": "docs"},
        {"title": "Django Girls Tutorial", "url": "https://tutorial.djangogirls.org/", "type": "tutorial"},
        {"title": "CS50W (Django module)", "url": "https://cs50.harvard.edu/web/", "type": "course"},
    ],
    "FastAPI": [
        {"title": "FastAPI Official Docs", "url": "https://fastapi.tiangolo.com/", "type": "docs"},
        {"title": "FastAPI Full Course - YouTube", "url": "https://www.youtube.com/watch?v=0sOvCWFmrtA", "type": "video"},
    ],
    "Docker": [
        {"title": "Docker Official Docs", "url": "https://docs.docker.com/", "type": "docs"},
        {"title": "Play with Docker", "url": "https://labs.play-with-docker.com/", "type": "interactive"},
        {"title": "Docker & Kubernetes Full Course - TechWorld with Nana", "url": "https://www.youtube.com/watch?v=3c-iBn73dDE", "type": "video"},
    ],
    "Machine Learning": [
        {"title": "fast.ai Practical Deep Learning", "url": "https://course.fast.ai/", "type": "course"},
        {"title": "Google ML Crash Course", "url": "https://developers.google.com/machine-learning/crash-course", "type": "course"},
        {"title": "CS229 - Stanford ML", "url": "https://cs229.stanford.edu/", "type": "course"},
    ],
    "SQL": [
        {"title": "SQLZoo", "url": "https://sqlzoo.net/", "type": "interactive"},
        {"title": "Mode SQL Tutorial", "url": "https://mode.com/sql-tutorial/", "type": "tutorial"},
        {"title": "PostgreSQL Official Docs", "url": "https://www.postgresql.org/docs/", "type": "docs"},
    ],
    "AWS": [
        {"title": "AWS Free Tier", "url": "https://aws.amazon.com/free/", "type": "platform"},
        {"title": "AWS Cloud Practitioner Essentials", "url": "https://aws.amazon.com/training/learn-about/cloud-practitioner/", "type": "course"},
        {"title": "A Cloud Guru - AWS", "url": "https://acloudguru.com/", "type": "course"},
    ],
    "Kubernetes": [
        {"title": "Kubernetes Docs", "url": "https://kubernetes.io/docs/", "type": "docs"},
        {"title": "KataCoda K8s", "url": "https://www.katacoda.com/courses/kubernetes", "type": "interactive"},
        {"title": "TechWorld with Nana - K8s", "url": "https://www.youtube.com/watch?v=X48VuDVv0do", "type": "video"},
    ],
    "TypeScript": [
        {"title": "TypeScript Handbook", "url": "https://www.typescriptlang.org/docs/handbook/", "type": "docs"},
        {"title": "Execute Program TypeScript", "url": "https://www.executeprogram.com/courses/typescript", "type": "interactive"},
    ],
    "default": [
        {"title": "MDN Web Docs", "url": "https://developer.mozilla.org/", "type": "docs"},
        {"title": "freeCodeCamp", "url": "https://www.freecodecamp.org/", "type": "course"},
        {"title": "The Odin Project", "url": "https://www.theodinproject.com/", "type": "course"},
    ],
}

INTERVIEW_TIPS = [
    "Practice explaining your project's architecture in 2 minutes (elevator pitch).",
    "Prepare for 'Tell me about a challenge you faced' — use STAR format (Situation, Task, Action, Result).",
    "Know the time/space complexity of key algorithms you used.",
    "Be ready to demo or screen-share your project during technical interviews.",
    "Understand WHY you chose each technology, not just what you used.",
    "Practice coding related concepts on LeetCode / HackerRank.",
    "Review system design basics if targeting mid-senior roles.",
    "⚠️ WARNING: You must be able to fully explain every line of your project. Recruiters WILL ask.",
]


def get_resources(skill: str) -> list[dict]:
    return RESOURCES_DB.get(skill, RESOURCES_DB["default"])[:3]


def generate_weekly_plan(committed_projects: list[dict], skill_gaps: list[dict], user_level: str = "fresher") -> dict:
    """Generate a personalized weekly roadmap for committed projects."""

    if not committed_projects:
        return {"weeks": [], "message": "No committed projects. Select a project to generate a roadmap."}

    project = committed_projects[0]  # Primary project
    skill = project.get("target_skill", "")
    path = project.get("skill_path", [])
    difficulty = project.get("difficulty", "Intermediate")
    estimated_time = project.get("estimated_time", "3 weeks")

    # Determine total weeks (normalize en-dash to hyphen for consistent matching)
    et = str(estimated_time or "3 weeks").replace("–", "-")
    if "4-5" in et or "5" in et:
        total_weeks = 5
    elif "3-4" in et or "4" in et:
        total_weeks = 4
    else:
        total_weeks = 3

    weeks = []

    # Week 1 — Foundation
    foundation_skill = path[0] if path else skill
    weeks.append({
        "week": 1,
        "theme": f"Foundation — {foundation_skill}",
        "tasks": [
            f"Complete official documentation tutorial for {foundation_skill}",
            f"Build 3 small exercises to solidify {foundation_skill} basics",
            "Set up GitHub repo with proper README",
            f"Watch 1–2 YouTube introductory videos on {foundation_skill}",
        ],
        "resources": get_resources(foundation_skill),
        "deliverable": f"Small {foundation_skill} mini-project pushed to GitHub",
    })

    # Week 2 — Bridge skill
    if len(path) >= 3:
        bridge_skill = path[1]
    else:
        bridge_skill = skill
    weeks.append({
        "week": 2,
        "theme": f"Bridge Skill — {bridge_skill}",
        "tasks": [
            f"Learn {bridge_skill} core concepts and install required tools",
            f"Build a simple {bridge_skill} demo app",
            "Integrate with Week 1 foundation skill",
            "Write a short blog or README explaining what you learned",
        ],
        "resources": get_resources(bridge_skill),
        "deliverable": f"Working {bridge_skill} integration demo",
    })

    # Week 3 — Main project build
    weeks.append({
        "week": 3,
        "theme": f"Build Project — {project['title']}",
        "tasks": [
            f"Scaffold project: {project['title']}",
            "Implement core features (focus on functionality first)",
            "Write unit tests for main components",
            "Push to GitHub with meaningful commit messages",
        ],
        "resources": get_resources(skill),
        "deliverable": "Working MVP of the project on GitHub",
    })

    # Week 4 — Polish & Deploy (if applicable)
    if total_weeks >= 4:
        weeks.append({
            "week": 4,
            "theme": "Polish, Tests & Deploy",
            "tasks": [
                "Add error handling and edge case coverage",
                "Write comprehensive README (setup, usage, screenshots)",
                "Deploy to Render / Railway / Vercel (free tier)",
                "Add project to portfolio/LinkedIn",
            ],
            "resources": [
                {"title": "Render (Free Hosting)", "url": "https://render.com/", "type": "platform"},
                {"title": "Railway (Free Hosting)", "url": "https://railway.app/", "type": "platform"},
                {"title": "How to Write a Great README", "url": "https://www.makeareadme.com/", "type": "guide"},
            ],
            "deliverable": "Deployed live project with proper documentation",
        })

    # Week 5 — Interview prep (if applicable)
    if total_weeks >= 5:
        weeks.append({
            "week": 5,
            "theme": "Interview Preparation",
            "tasks": [
                f"Practice explaining the {skill} project in 2 minutes",
                "Solve 10 LeetCode Easy/Medium problems related to the domain",
                "Mock interview: Record yourself answering common questions",
                "Update resume with approved project and new skills",
            ],
            "resources": [
                {"title": "LeetCode", "url": "https://leetcode.com/", "type": "practice"},
                {"title": "Pramp Mock Interviews", "url": "https://www.pramp.com/", "type": "practice"},
                {"title": "Tech Interview Handbook", "url": "https://www.techinterviewhandbook.org/", "type": "guide"},
            ],
            "deliverable": "Interview-ready with documented project",
        })

    total_gap_skills = len([g for g in skill_gaps if g.get("reachable")])

    return {
        "target_skill": skill,
        "project_title": project["title"],
        "estimated_duration": f"{total_weeks} weeks",
        "user_level": user_level,
        "skill_path": path,
        "tech_stack": project.get("tech_stack", []),
        "weeks": weeks,
        "interview_tips": INTERVIEW_TIPS,
        "interview_warning": (
            "⚠️ Be ready to explain every part of this project. "
            "Interviewers WILL ask about your architecture decisions, bugs you faced, and how you solved them. "
            "Never add a project you can't fully explain."
        ),
        "total_skills_to_learn": total_gap_skills,
        "project": project,
    }

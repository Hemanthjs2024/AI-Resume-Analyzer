"""
Project Suggestion Engine
Generates buildable project suggestions based on valid skill paths only.
"""

import logging

logger = logging.getLogger("resume-agent.project_suggester")

PROJECT_TEMPLATES = {
    "Selenium": {
        "title": "Automated Web Testing Suite",
        "description": "Build a full automated test suite for an e-commerce website covering login, product search, cart, and checkout flows.",
        "tech_stack": ["Python", "Selenium", "Pytest", "HTML Report"],
        "estimated_time": "2–3 weeks",
        "difficulty": "Beginner",
        "why_relevant": "Demonstrates real-world Selenium usage that directly matches the JD requirement.",
        "github_topics": ["selenium", "automation", "testing"],
    },
    "Playwright": {
        "title": "Cross-Browser E2E Testing Framework",
        "description": "Create an end-to-end testing framework for a React app using Playwright across Chrome, Firefox, and Safari.",
        "tech_stack": ["Node.js", "Playwright", "TypeScript", "CI/CD"],
        "estimated_time": "3 weeks",
        "difficulty": "Intermediate",
        "why_relevant": "Shows modern E2E testing skills and CI/CD integration.",
        "github_topics": ["playwright", "e2e-testing", "typescript"],
    },
    "React": {
        "title": "Full-Stack Task Management Dashboard",
        "description": "Build a responsive task management app with React frontend, drag-and-drop, dark mode, and REST API integration.",
        "tech_stack": ["React", "TypeScript", "Redux", "Node.js", "MongoDB"],
        "estimated_time": "3–4 weeks",
        "difficulty": "Intermediate",
        "why_relevant": "Covers core React patterns (state, hooks, routing) recruiters look for.",
        "github_topics": ["react", "typescript", "fullstack"],
    },
    "Next.js": {
        "title": "Blog Platform with SSR",
        "description": "Build a full-featured blog with Next.js, SSR, dynamic routing, SEO optimization, and a CMS backend.",
        "tech_stack": ["Next.js", "TypeScript", "PostgreSQL", "Prisma"],
        "estimated_time": "3–4 weeks",
        "difficulty": "Intermediate",
        "why_relevant": "Demonstrates SSR, SEO handling, and full-stack Next.js development.",
        "github_topics": ["nextjs", "ssr", "blog"],
    },
    "Machine Learning": {
        "title": "Customer Churn Prediction Model",
        "description": "Build an end-to-end ML pipeline: data cleaning, feature engineering, model training, evaluation, and a Flask API deployment.",
        "tech_stack": ["Python", "Pandas", "Scikit-learn", "Flask", "Docker"],
        "estimated_time": "4 weeks",
        "difficulty": "Intermediate",
        "why_relevant": "Mirrors a real production ML workflow from data to deployment.",
        "github_topics": ["machine-learning", "scikit-learn", "flask"],
    },
    "Docker": {
        "title": "Containerized Microservices App",
        "description": "Containerize a multi-service application (API + DB + Redis) using Docker Compose with a CI/CD pipeline.",
        "tech_stack": ["Docker", "Docker Compose", "GitHub Actions", "Redis"],
        "estimated_time": "2–3 weeks",
        "difficulty": "Intermediate",
        "why_relevant": "Shows practical Docker and DevOps skills that match your gap.",
        "github_topics": ["docker", "microservices", "devops"],
    },
    "Kubernetes": {
        "title": "Kubernetes Deployment with Auto-scaling",
        "description": "Deploy a web application to a local Kubernetes cluster (Minikube) with HPA, load balancing, and monitoring.",
        "tech_stack": ["Kubernetes", "Docker", "Prometheus", "Grafana"],
        "estimated_time": "4–5 weeks",
        "difficulty": "Advanced",
        "why_relevant": "Demonstrates production-grade K8s deployment skills.",
        "github_topics": ["kubernetes", "devops", "monitoring"],
    },
    "AWS": {
        "title": "Serverless REST API on AWS Lambda",
        "description": "Build and deploy a serverless REST API using AWS Lambda, API Gateway, DynamoDB, and S3 with IaC via CloudFormation.",
        "tech_stack": ["AWS Lambda", "API Gateway", "DynamoDB", "Python", "CloudFormation"],
        "estimated_time": "3–4 weeks",
        "difficulty": "Intermediate",
        "why_relevant": "Directly maps to AWS cloud skills required in the JD.",
        "github_topics": ["aws", "serverless", "lambda"],
    },
    "FastAPI": {
        "title": "High-Performance REST API with Auth",
        "description": "Build a production-ready REST API with FastAPI, JWT auth, PostgreSQL, background tasks, and OpenAPI docs.",
        "tech_stack": ["FastAPI", "PostgreSQL", "Redis", "Docker", "Pytest"],
        "estimated_time": "3 weeks",
        "difficulty": "Intermediate",
        "why_relevant": "Shows async Python backend skills with modern best practices.",
        "github_topics": ["fastapi", "rest-api", "python"],
    },
    "TensorFlow": {
        "title": "Image Classification Web App",
        "description": "Train a CNN to classify images, deploy it as a web app with FastAPI backend and React frontend.",
        "tech_stack": ["Python", "TensorFlow", "FastAPI", "React", "Docker"],
        "estimated_time": "4–5 weeks",
        "difficulty": "Advanced",
        "why_relevant": "End-to-end deep learning project demonstrating production ML deployment.",
        "github_topics": ["tensorflow", "deep-learning", "computer-vision"],
    },
    "NLP": {
        "title": "Sentiment Analysis API",
        "description": "Build a sentiment analysis API trained on custom data with a preprocessing pipeline, model evaluation, and REST endpoint.",
        "tech_stack": ["Python", "NLTK", "Scikit-learn", "FastAPI", "Docker"],
        "estimated_time": "3 weeks",
        "difficulty": "Intermediate",
        "why_relevant": "Demonstrates NLP skills from data preprocessing to deployment.",
        "github_topics": ["nlp", "sentiment-analysis", "fastapi"],
    },
    "GraphQL": {
        "title": "GraphQL Social Media API",
        "description": "Build a GraphQL API for a social platform with users, posts, comments, and real-time subscriptions.",
        "tech_stack": ["Node.js", "GraphQL", "PostgreSQL", "Prisma"],
        "estimated_time": "3–4 weeks",
        "difficulty": "Intermediate",
        "why_relevant": "Demonstrates modern API design using GraphQL.",
        "github_topics": ["graphql", "nodejs", "api"],
    },
    "CI/CD": {
        "title": "Full CI/CD Pipeline Setup",
        "description": "Set up a complete CI/CD pipeline with GitHub Actions: lint, test, build, containerize, and deploy to cloud.",
        "tech_stack": ["GitHub Actions", "Docker", "AWS/GCP", "SonarQube"],
        "estimated_time": "2 weeks",
        "difficulty": "Intermediate",
        "why_relevant": "Core DevOps skill showing automation from commit to production.",
        "github_topics": ["ci-cd", "github-actions", "devops"],
    },
    "MongoDB": {
        "title": "Real-Time Chat App with MongoDB",
        "description": "Build a real-time chat application with Node.js, Socket.io, MongoDB for message persistence, and React frontend.",
        "tech_stack": ["Node.js", "Socket.io", "MongoDB", "React"],
        "estimated_time": "3–4 weeks",
        "difficulty": "Intermediate",
        "why_relevant": "Demonstrates NoSQL, real-time communication, and full-stack skills.",
        "github_topics": ["mongodb", "real-time", "chat"],
    },
}

_DEFAULT_PROJECT = {
    "title": "Portfolio API Project",
    "description": "Build a complete REST API project showcasing the target skill, with proper documentation and tests.",
    "tech_stack": [],
    "estimated_time": "3 weeks",
    "difficulty": "Intermediate",
    "why_relevant": "Demonstrates the skill through a real, deployable project.",
    "github_topics": [],
}


from .llm_client import suggest_projects_llm

def suggest_projects(gaps: list[dict], user_skills: list[str], jd_text: str = "") -> list[dict]:
    """
    Generate project suggestions using LLM for better relevance.
    """
    # 1. Identify top gaps to bridge
    top_gaps = [g["skill"] for g in gaps if g.get("reachable")][:5]
    
    # 2. Try LLM generation first
    try:
        dynamic_projects = suggest_projects_llm(user_skills, jd_text, top_gaps)
        if dynamic_projects and len(dynamic_projects) > 0:
            # Add 'committed' flag
            for p in dynamic_projects:
                p["committed"] = False
            return dynamic_projects[:5]
    except Exception as e:
        logger.warning("LLM project suggestion failed, falling back: %s", e)

    # 3. Fallback to template/rule-based logic
    suggestions = []
    seen_titles = set()

    for gap in gaps:
        if not gap.get("reachable"):
            continue

        skill = gap["skill"]
        path = gap["path"]

        template = PROJECT_TEMPLATES.get(skill)
        if not template:
            # Generic fallback
            template = {**_DEFAULT_PROJECT, "title": f"{skill} Showcase Project"}
            template["tech_stack"] = path[-3:] if len(path) >= 3 else path
            template["why_relevant"] = f"Directly builds your {skill} skill using your existing {', '.join(path[:2])} knowledge."

        if template["title"] in seen_titles:
            continue
        seen_titles.add(template["title"])

        suggestions.append({
            **template,
            "target_skill": skill,
            "skill_path": path,
            "confidence": gap["confidence"],
            "risk": gap["risk"],
            "committed": False,
        })

    suggestions.sort(key=lambda s: -s.get("confidence", 0))
    return suggestions[:5]

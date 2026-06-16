# AI Career Alignment Agent

#To start the Backend:

Open a terminal and cd d:\Resume-Agent\backend
Run .\venv\Scripts\activate
Run uvicorn main:app --reload

#To start the Frontend:

Open a new terminal and cd d:\Resume-Agent\frontend
Run npm run dev


An intelligent, full-stack career assistant that analyzes resumes against job descriptions using a **rule-based Skill Graph + LLM hybrid** approach. It goes beyond a simple keyword matcher by intelligently detecting skill paths to calculate confidence limits and suggesting relevant projects.

## Project Structure
- `backend/` - FastAPI python server handling skill graph BFS logic, AI integrations, file parsing, and file generation.
- `frontend/` - React frontend built with Vite, TailwindCSS (v4), Framer Motion, and Zustand global state management.

## Setup Instructions

### Backend Setup
1. Navigate to `backend/` directory
2. Create virtual environment: `python -m venv venv`
3. Activate venv:
   - Windows: `.\venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. (Optional but recommended) copy `.env.example` to `.env` and add your `OPENAI_API_KEY`. Without it, intelligent mock fallback responses are used.
6. Start backend: `uvicorn main:app --reload`
   - Available at: `http://localhost:8000`

### Frontend Setup
1. Navigate to `frontend/` directory
2. Install dependencies: `npm install`
3. Run dev server: `npm run dev`
4. Open the UI: `http://localhost:5173`

## Core Features
1. **Resume + JD Parser:** Extracts text from PDF/DOCX and job descriptions.
2. **Skill Graph Engine:** A BFS-powered engine matching user skills to target skills to realistically estimate time and capability required to jump gaps.
3. **Project Suggestions:** Generates project ideas based *only* on reachable skill paths.
4. **Roadmap Generator:** Auto-generates week-by-week career goals if you commit to learning new skills.
5. **AI Resume Optimizer:** Analyzes and optimizes experience bullets.
6. **Built-in Score Engine:** Calculates real, actionable improvement percentages.
7. **ATS-Generator:** Generates a 100% text-based DOCX file and PDF file containing no formatting tricks that would block ATS systems.

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE,
});

export const analyzeResume = async (file, jdText) => {
  const formData = new FormData();
  formData.append('resume', file);
  formData.append('jd_text', jdText);
  const response = await api.post('/api/analyse', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const generateResume = async (reviewItems, committedProjects, selectedSkills, candidateName, template, structuredData) => {
  const response = await api.post('/api/generate', {
    review_items: reviewItems,
    committed_projects: committedProjects,
    selected_skills: selectedSkills || [],
    candidate_name: candidateName,
    template: template,
    structured_data: structuredData,
  });
  return response.data;
};

export const generateRoadmap = async (committedProjects, skillGaps) => {
  const response = await api.post('/api/roadmap', {
    committed_projects: committedProjects,
    skill_gaps: skillGaps,
    user_level: 'fresher',
  });
  return response.data;
};

export const chatWithAgent = async (message, resumeContext, jdContext) => {
  const response = await api.post('/api/chat', {
    message,
    resume_context: resumeContext,
    jd_context: jdContext,
  });
  return response.data;
};

export const getDownloadUrl = (filename) => `${API_BASE}/api/download/${filename}`;

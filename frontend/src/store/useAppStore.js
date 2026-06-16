import { create } from 'zustand';

const useAppStore = create((set) => ({
  // Navigation State
  currentStep: 1,
  setStep: (step) => set({ currentStep: step }),
  nextStep: () => set((state) => ({ currentStep: Math.min(state.currentStep + 1, 6) })),
  prevStep: () => set((state) => ({ currentStep: Math.max(state.currentStep - 1, 1) })),

  // Input Data
  resumeFile: null,
  setResumeFile: (file) => set({ resumeFile: file }),
  jdText: '',
  setJdText: (text) => set({ jdText: text }),

  // Analysis Data
  analysisResult: null,
  setAnalysisResult: (data) => set({ analysisResult: data }),

  // Review & Projects Data
  reviewItems: [], // [{ section, original, optimized, status, edited_content }]
  setReviewItems: (items) => set({ reviewItems: items }),
  updateReviewItem: (section, updates) => set((state) => ({
    reviewItems: state.reviewItems.map(item =>
      item.section === section ? { ...item, ...updates } : item
    )
  })),

  committedProjects: [],
  setCommittedProjects: (projects) => set({ committedProjects: projects }),
  toggleProjectCommitment: (title) => set((state) => ({
    committedProjects: state.committedProjects.map(p =>
      p.title === title ? { ...p, committed: !p.committed } : p
    )
  })),

  selectedSkills: [],
  setSelectedSkills: (skills) => set({ selectedSkills: skills }),
  toggleSkillSelection: (skill) => set((state) => {
    const isSelected = state.selectedSkills.includes(skill);
    return {
      selectedSkills: isSelected 
        ? state.selectedSkills.filter(s => s !== skill)
        : [...state.selectedSkills, skill]
    };
  }),

  // Generation Data
  generatedFiles: null, // { docx_filename, pdf_filename, pdf_available }
  setGeneratedFiles: (files) => set({ generatedFiles: files }),

  // Roadmap Data
  roadmap: null,
  setRoadmap: (data) => set({ roadmap: data }),

  // Global Loading State
  isLoading: false,
  setIsLoading: (status) => set({ isLoading: status }),

  // Reset
  resetApp: () => set({
    currentStep: 1,
    resumeFile: null,
    jdText: '',
    analysisResult: null,
    reviewItems: [],
    committedProjects: [],
    selectedSkills: [],
    generatedFiles: null,
    roadmap: null,
    isLoading: false,
  })
}));

export default useAppStore;

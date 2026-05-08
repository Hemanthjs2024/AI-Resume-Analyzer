import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, ChevronLeft, Loader2, Sparkles, CheckSquare, Settings, CheckCircle2, Eye } from 'lucide-react';
import useAppStore from '../store/useAppStore';
import { generateResume } from '../api/client';

// ── Visual Template Previews ──────────────────────────────────────────────────

const SECTION_LABELS = {
  "summary": "Profile Summary",
  "work_experience": "Work Experience",
  "internships": "Internships",
  "technical_skills": "Technical Skills",
  "core_competencies": "Core Competencies",
  "projects": "Projects",
  "education": "Education",
  "certifications": "Certifications",
  "awards": "Awards",
  "interests": "Interests",
};

const TEMPLATE_STRUCTURES = {
  "chronological_classic": ["summary", "work_experience", "internships", "technical_skills", "projects", "education", "certifications", "awards", "interests"],
  "modern_minimal": ["summary", "core_competencies", "technical_skills", "work_experience", "internships", "projects", "education", "certifications", "interests"],
  "skills_projects": ["summary", "technical_skills", "projects", "internships", "work_experience", "education", "certifications", "interests"],
  "executive_leadership": ["summary", "core_competencies", "work_experience", "internships", "awards", "education", "certifications", "interests"],
};

const TemplatePreview = ({ type }) => {
  const sections = TEMPLATE_STRUCTURES[type] || [];

  return (
    <div className="flex flex-col gap-1 p-2 bg-slate-900 rounded-lg w-full h-full overflow-y-auto">
      <div className="text-center mb-1">
        <div className="h-1 w-16 bg-slate-500 rounded mx-auto" />
        <div className="h-[1px] w-12 bg-slate-500/60 rounded mx-auto mt-0.5" />
      </div>
      {sections.map((sec, idx) => (
        <div key={idx} className="flex items-center gap-1 mb-0.5">
          <div className={`h-1 rounded-sm ${idx % 2 === 0 ? 'bg-slate-500' : 'bg-slate-600/50'}`}
            style={{ width: sec.includes('summary') ? '100%' : 'calc(100% - 8px)', marginLeft: sec.includes('summary') ? 0 : 8 }}
          />
          <span className="text-[5px] text-slate-400 uppercase font-bold tracking-widest whitespace-nowrap flex-shrink-0">
            {SECTION_LABELS[sec] || sec}
          </span>
        </div>
      ))}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────

const TEMPLATES = [
  {
    id: 'chronological_classic',
    label: 'Chronological Classic',
    tag: 'Best for Experience',
    tagColor: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
    desc: 'Traditional format with reverse-chronological work history. Most widely accepted by ATS systems and hiring managers.',
    highlights: ['Work History First', 'ATS Optimized', 'Corporate & IT Roles'],
  },
  {
    id: 'modern_minimal',
    label: 'Modern Minimal',
    tag: 'Most Popular',
    tagColor: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
    desc: 'Clean, contemporary layout that balances skills and experience. Perfect for mid-level professionals in tech.',
    highlights: ['Balanced Layout', 'Skills Upfront', 'Clean ATS Format'],
  },
  {
    id: 'skills_projects',
    label: 'Skills & Projects',
    tag: 'Best for Freshers',
    tagColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    desc: 'Leads with technical skills and projects. Ideal for freshers, career switchers, and candidates with strong portfolio.',
    highlights: ['Projects Highlighted', 'Skills First', 'Portfolio Focused'],
  },
  {
    id: 'executive_leadership',
    label: 'Executive Leadership',
    tag: 'Senior Roles',
    tagColor: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    desc: 'Authoritative, achievement-focused format designed for managers, team leads, and senior professionals.',
    highlights: ['Leadership Focus', 'Impact-Driven', 'Senior Positions'],
  },
];

// ─────────────────────────────────────────────────────────────────────────────

export default function GenerateStep() {
  const { reviewItems, committedProjects, selectedSkills, analysisResult, prevStep, nextStep, setGeneratedFiles } = useAppStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [template, setTemplate] = useState('chronological_classic');
  const [previewTemplate, setPreviewTemplate] = useState(null);

  const finalReviewItems = (reviewItems || []).map(item =>
    item.status === 'pending' ? { ...item, status: 'accepted' } : item
  );

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError('');
    try {
      const result = await generateResume(
        finalReviewItems,
        committedProjects || [],
        selectedSkills || [],
        analysisResult?.candidate_name || "Professional",
        template,
        analysisResult?.structured_data
      );
      setGeneratedFiles(result);
      nextStep();
    } catch (err) {
      console.error(err);
      setError('Failed to generate resume. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const committedOnes = (committedProjects || []).filter(p => p.committed);
  const selected = TEMPLATES.find(t => t.id === template);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex flex-col h-full space-y-6 pb-10 overflow-y-auto pr-1 custom-scrollbar"
    >
      {/* Header */}
      <div className="flex flex-col items-center text-center space-y-2 pt-2">
        <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center shadow-xl shadow-cyan-500/20">
          <Sparkles className="w-7 h-7 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Finalize & Generate</h2>
        <p className="text-slate-400 text-sm">Choose a template and we'll build your ATS-optimized resume.</p>
      </div>

      {/* Template Grid */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Settings className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-widest">Select Template</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {TEMPLATES.map(t => (
            <motion.button
              key={t.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setTemplate(t.id)}
              className={`relative text-left rounded-2xl border transition-all overflow-hidden flex flex-col ${
                template === t.id
                  ? 'border-cyan-500/60 ring-1 ring-cyan-500/30 bg-slate-800/80'
                  : 'border-slate-700/50 bg-slate-800/30 hover:border-slate-600'
              }`}
            >
              {/* Visual Preview */}
              <div className="relative h-44 p-2 bg-slate-950/60">
                <TemplatePreview type={t.id} />
                {template === t.id && (
                  <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-cyan-500 flex items-center justify-center shadow-lg">
                    <CheckCircle2 className="w-4 h-4 text-white" />
                  </div>
                )}
                <button
                  onClick={(e) => { e.stopPropagation(); setPreviewTemplate(previewTemplate === t.id ? null : t.id); }}
                  className="absolute bottom-2 right-2 px-2 py-0.5 rounded text-[9px] bg-slate-700/80 text-slate-300 hover:bg-slate-600/80 flex items-center gap-1 border border-slate-600/50"
                >
                  <Eye className="w-2.5 h-2.5" /> Info
                </button>
              </div>

              {/* Info */}
              <div className="p-3 flex flex-col gap-1.5 flex-1">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-xs font-bold text-white leading-tight">{t.label}</span>
                  <span className={`text-[9px] px-1.5 py-0.5 rounded border font-bold uppercase tracking-wide flex-shrink-0 ${t.tagColor}`}>
                    {t.tag}
                  </span>
                </div>
                <AnimatePresence>
                  {previewTemplate === t.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="overflow-hidden"
                    >
                      <p className="text-[10px] text-slate-400 leading-relaxed mt-1">{t.desc}</p>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {t.highlights.map(h => (
                          <span key={h} className="text-[9px] px-1.5 py-0.5 rounded bg-slate-700/50 text-slate-300 border border-slate-600/30">{h}</span>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Committed Changes Summary */}
      <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 p-5">
        <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4 uppercase tracking-widest">
          <CheckSquare className="w-4 h-4 text-indigo-400" /> What's Being Added
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="text-[10px] font-black text-slate-500 uppercase tracking-[0.15em] border-b border-slate-700 pb-1 mb-2">
              Target Skills ({selectedSkills?.length || 0})
            </div>
            <div className="flex flex-wrap gap-1.5">
              {(selectedSkills || []).map(s => (
                <span key={s} className="px-2 py-0.5 bg-indigo-500/10 border border-indigo-500/20 rounded text-[11px] text-indigo-300 font-medium">{s}</span>
              ))}
              {(!selectedSkills || selectedSkills.length === 0) && (
                <span className="text-xs text-slate-500 italic">No new skills selected.</span>
              )}
            </div>
          </div>
          <div>
            <div className="text-[10px] font-black text-slate-500 uppercase tracking-[0.15em] border-b border-slate-700 pb-1 mb-2">
              Strategic Projects ({committedOnes.length})
            </div>
            <div className="space-y-1.5">
              {committedOnes.map(p => (
                <div key={p.title} className="flex items-start gap-2 p-2 bg-slate-900/50 rounded-lg border border-slate-700/30">
                  <CheckCircle2 className="w-3 h-3 text-cyan-400 mt-0.5 flex-shrink-0" />
                  <span className="text-xs text-slate-200 leading-tight">{p.title}</span>
                </div>
              ))}
              {committedOnes.length === 0 && <span className="text-xs text-slate-500 italic">No projects committed.</span>}
            </div>
          </div>
        </div>
        <div className="mt-4 flex items-center gap-2 text-xs text-emerald-400/80 bg-emerald-500/5 p-3 rounded-xl border border-emerald-500/10">
          <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" />
          All original resume sections (Education, Experience, Projects, Skills) will be preserved and merged.
        </div>
      </div>

      {/* Action Bar */}
      <div className="flex items-center justify-between gap-4 pt-2 border-t border-slate-700/50">
        <button onClick={prevStep} disabled={isGenerating} className="px-4 py-2 text-slate-400 hover:text-white text-xs font-bold uppercase tracking-widest flex items-center gap-1">
          <ChevronLeft className="w-4 h-4" /> Back
        </button>

        <div className="flex flex-col items-end gap-2">
          {error && (
            <div className="px-3 py-1.5 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-xs">{error}</div>
          )}
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="px-8 py-3 bg-gradient-to-r from-indigo-500 to-cyan-500 hover:from-indigo-400 hover:to-cyan-400 text-white rounded-xl font-bold text-sm flex items-center gap-2 transition-all hover:scale-[1.02] active:scale-95 disabled:opacity-50 shadow-lg shadow-indigo-500/20"
          >
            {isGenerating ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Building Resume...</>
            ) : (
              <><Sparkles className="w-4 h-4" /> Generate with {selected?.label} <ChevronRight className="w-4 h-4" /></>
            )}
          </button>
        </div>
      </div>
    </motion.div>
  );
}

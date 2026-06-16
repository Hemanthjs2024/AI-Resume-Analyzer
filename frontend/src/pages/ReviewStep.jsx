import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, X, Edit2, ChevronRight, ChevronLeft, Save, User, Cpu, Briefcase, Target, Sparkles, CheckCircle2 } from 'lucide-react';
import useAppStore from '../store/useAppStore';

export default function ReviewStep() {
  const { reviewItems, committedProjects, selectedSkills, updateReviewItem, prevStep, nextStep } = useAppStore();
  const [editingKey, setEditingKey] = useState(null);
  const [editDraft, setEditDraft] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (editingKey && textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [editDraft, editingKey]);

  const handleAction = (section, action, content = null) => {
    if (action === 'accepted') {
      updateReviewItem(section, { status: 'accepted' });
    } else if (action === 'rejected') {
      updateReviewItem(section, { status: 'rejected' });
    } else if (action === 'edited') {
      updateReviewItem(section, { status: 'edited', edited_content: content });
      setEditingKey(null);
    }
  };

  const startEdit = (item) => {
    setEditingKey(item.section);
    setEditDraft(item.edited_content || item.optimized);
  };

  const categories = [
    { id: 'summary', label: 'Profile Summary', icon: <User className="w-5 h-5" />, sectionKeys: ['summary'] },
    { id: 'skills', label: 'Skill Set', icon: <Cpu className="w-5 h-5" />, sectionKeys: ['skills'] },
    { id: 'experience', label: 'Work Experience', icon: <Briefcase className="w-5 h-5" />, sectionKeys: ['experience'] },
    { id: 'projects', label: 'Projects', icon: <Target className="w-5 h-5" />, sectionKeys: ['projects'] },
    { id: 'others', label: 'Additional Info', icon: <Sparkles className="w-5 h-5" />, sectionKeys: ['education', 'certifications', 'achievements'] }
  ];

  const committedOnes = committedProjects.filter(p => p.committed);

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex flex-col h-full space-y-6 overflow-hidden"
    >
      <div className="text-center space-y-2 flex-shrink-0">
        <h2 className="text-2xl font-bold text-white tracking-tight">Review AI Optimizations</h2>
        <p className="text-slate-400">Your resume is organized into categories. Review and approve changes for each.</p>
      </div>

      {/* Global Optimization Summary (Top of Review) */}
      {(selectedSkills.length > 0 || committedOnes.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-shrink-0">
          {selectedSkills.length > 0 && (
            <div className="bg-indigo-500/10 border border-indigo-500/20 p-4 rounded-2xl">
              <div className="text-[10px] font-black text-indigo-400 uppercase tracking-widest flex items-center gap-2 mb-2">
                <Sparkles className="w-3 h-3" /> Targeted Keywords Added
              </div>
              <div className="flex flex-wrap gap-2">
                {selectedSkills.slice(0, 8).map(s => (
                  <span key={s} className="px-2 py-0.5 bg-slate-900/40 rounded text-[10px] text-slate-300">{s}</span>
                ))}
                {selectedSkills.length > 8 && <span className="text-[10px] text-slate-500">+{selectedSkills.length - 8} more</span>}
              </div>
            </div>
          )}
          {committedOnes.length > 0 && (
            <div className="bg-cyan-500/10 border border-cyan-500/20 p-4 rounded-2xl">
              <div className="text-[10px] font-black text-cyan-400 uppercase tracking-widest flex items-center gap-2 mb-2">
                <Sparkles className="w-3 h-3" /> Strategic Projects Added
              </div>
              <div className="flex flex-wrap gap-2">
                {committedOnes.map(p => (
                  <span key={p.title} className="px-2 py-0.5 bg-slate-900/40 rounded text-[10px] text-slate-300 line-clamp-1">{p.title}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="flex-1 overflow-y-auto space-y-12 pr-2 pb-24 custom-scrollbar">
        {categories.map((cat) => {
          const items = reviewItems.filter(i => cat.sectionKeys.includes(i.section));
          const hasCommitted = cat.id === 'projects' && committedOnes.length > 0;
          const hasSelected = cat.id === 'skills' && selectedSkills.length > 0;
          
          if (items.length === 0 && !hasCommitted && !hasSelected) return null;

          return (
            <div key={cat.id} className="space-y-4">
              <div className="flex items-center gap-2 px-2">
                <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
                  {cat.icon}
                </div>
                <h3 className="text-lg font-bold text-slate-100">{cat.label}</h3>
                <div className="h-px flex-1 bg-gradient-to-r from-slate-700/50 to-transparent ml-2"></div>
              </div>

              <div className="grid grid-cols-1 gap-4 bg-slate-800/20 p-4 rounded-2xl border border-slate-700/30">
                {/* Show Selected Skills in the Skill Set Section */}
                {cat.id === 'skills' && selectedSkills.length > 0 && (
                  <div className="mb-4 space-y-3 bg-indigo-500/5 p-4 rounded-xl border border-indigo-500/10">
                    <div className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest flex items-center gap-2">
                      <Sparkles className="w-3 h-3" /> Targeted Keywords to be Integrated
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {selectedSkills.map((skill, sidx) => (
                        <div key={sidx} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300">
                          <CheckCircle2 className="w-3.5 h-3.5" /> {skill}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {items.map((item, idx) => (
                  <div key={idx} className="bg-slate-800/40 rounded-xl border border-slate-700/50 overflow-hidden shadow-sm mb-10 last:mb-0">
                    {/* Header */}
                    <div className="px-4 py-2.5 border-b border-slate-700/50 flex justify-between items-center bg-slate-800/80 text-slate-300">
                      <span className="text-xs font-bold uppercase tracking-wider">{item.label}</span>
                    </div>

                    {/* Content */}
                    <div className="p-4 bg-slate-900/30">
                      {item.note && (
                        <div className="mb-3 text-xs text-cyan-400/80 italic flex items-center gap-1.5">
                          <Sparkles className="w-3 h-3" /> {item.note}
                        </div>
                      )}
                      
                      {editingKey === item.section ? (
                        <div className="space-y-3">
                          <textarea
                            ref={textareaRef}
                            value={editDraft}
                            onChange={(e) => {
                              setEditDraft(e.target.value);
                              e.target.style.height = 'auto';
                              e.target.style.height = e.target.scrollHeight + 'px';
                            }}
                            className="w-full bg-slate-800 text-slate-200 border border-indigo-500/50 rounded-lg p-3 min-h-[200px] text-sm outline-none focus:ring-2 ring-indigo-500/50 overflow-hidden resize-none"
                          />
                          <div className="flex justify-end gap-2">
                            <button onClick={() => setEditingKey(null)} className="px-3 py-1.5 text-xs rounded bg-slate-700 text-slate-300 hover:bg-slate-600">Cancel</button>
                            <button onClick={() => handleAction(item.section, 'edited', editDraft)} className="px-3 py-1.5 text-xs rounded bg-indigo-500 text-white hover:bg-indigo-400 flex items-center gap-1"><Save className="w-3.5 h-3.5"/> Save Changes</button>
                          </div>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          <div className="text-sm text-slate-200 whitespace-pre-wrap font-sans leading-relaxed">
                            {item.status === 'edited' ? (item.edited_content || item.original) : (item.optimized || item.original)}
                          </div>

                       {/* Action Buttons */}
                           {editingKey !== item.section && item.status === 'pending' && (
                             <div className="pt-3 border-t border-slate-700/30 flex gap-2 justify-end">
                               <button onClick={() => handleAction(item.section, 'rejected')} className="flex items-center gap-1 px-3 py-1 rounded-md text-xs font-medium text-slate-400 hover:bg-slate-800 transition-colors">
                                 <X className="w-3.5 h-3.5" /> Skip
                               </button>
                               <button onClick={() => startEdit(item)} className="flex items-center gap-1 px-3 py-1 rounded-md text-xs font-medium text-indigo-400 hover:bg-indigo-500/10 transition-colors">
                                 <Edit2 className="w-3.5 h-3.5" /> Edit
                               </button>
                               <button onClick={() => handleAction(item.section, 'accepted')} className="flex items-center gap-1 px-4 py-1.5 rounded-md text-xs font-bold bg-green-500/10 text-green-400 hover:bg-green-500/20 transition-colors border border-green-500/20">
                                 <Check className="w-3.5 h-3.5" /> Approve Optimization
                               </button>
                             </div>
                           )}
                           {editingKey !== item.section && (item.status === 'accepted' || item.status === 'edited') && (
                             <div className="pt-3 border-t border-green-500/20 flex gap-2 justify-end">
                               <button onClick={() => startEdit(item)} className="flex items-center gap-1 px-3 py-1 rounded-md text-xs font-medium text-indigo-400 hover:bg-indigo-500/10 transition-colors">
                                 <Edit2 className="w-3.5 h-3.5" /> Edit
                               </button>
                             </div>
                           )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {/* Show Committed Projects in the Projects Section */}
                {cat.id === 'projects' && committedOnes.length > 0 && (
                  <div className="mt-4 space-y-3 bg-cyan-500/5 p-4 rounded-xl border border-cyan-500/10">
                    <div className="text-[10px] font-bold text-cyan-500 uppercase tracking-widest flex items-center gap-2">
                      <Sparkles className="w-3 h-3" /> Strategic Projects to be Added
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      {committedOnes.map((proj, pidx) => (
                        <div key={pidx} className="p-4 rounded-xl bg-slate-900/40 border border-cyan-500/20 flex flex-col gap-2">
                          <div className="flex justify-between items-start">
                            <h4 className="text-sm font-bold text-cyan-300">{proj.title}</h4>
                            <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                          </div>
                          <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">{proj.description}</p>
                          <div className="flex flex-wrap gap-1.5 mt-1">
                            {proj.tech_stack.slice(0, 3).map((tech, ti) => (
                              <span key={ti} className="px-1.5 py-0.5 rounded bg-slate-800 text-[9px] text-slate-300 border border-slate-700">{tech}</span>
                            ))}
                            {proj.tech_stack.length > 3 && <span className="text-[9px] text-slate-500">+{proj.tech_stack.length - 3}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Action Bar (Fixed at bottom) */}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-slate-900/90 backdrop-blur-md border-t border-slate-800 flex justify-between items-center z-10 rounded-b-2xl shadow-[0_-10px_20px_-10px_rgba(0,0,0,0.5)]">
        <button onClick={prevStep} className="px-6 py-2 text-slate-400 hover:text-white rounded-lg font-medium flex items-center gap-2 transition-colors">
          <ChevronLeft className="w-4 h-4" /> Back
        </button>
        <button onClick={nextStep} className="px-8 py-2.5 bg-gradient-to-r from-indigo-500 to-cyan-500 hover:from-indigo-400 hover:to-cyan-400 text-white rounded-lg font-bold flex items-center gap-2 transition-transform hover:scale-[1.02] active:scale-95 shadow-lg shadow-indigo-500/20">
          Proceed to Generate <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  );
}

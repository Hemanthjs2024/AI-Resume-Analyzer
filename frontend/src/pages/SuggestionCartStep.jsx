import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Target, Cpu, ShoppingCart, CheckCircle2, Plus, X, ChevronRight, ChevronLeft, Sparkles, Send } from 'lucide-react';
import useAppStore from '../store/useAppStore';

export default function SuggestionCartStep() {
  const { analysisResult, selectedSkills, toggleSkillSelection, committedProjects, toggleProjectCommitment, prevStep, nextStep } = useAppStore();
  const [inputText, setInputText] = useState('');

  if (!analysisResult) return null;

  const { gap_analysis } = analysisResult;

    const gaps = gap_analysis?.gaps || [];
    const handleParseInput = () => {
    if (!inputText.trim()) return;
    const lowerInput = inputText.toLowerCase();
    
    let addedSomething = false;

    gaps.forEach(gap => {
      if (lowerInput.includes(gap.skill.toLowerCase()) && !selectedSkills.includes(gap.skill)) {
        toggleSkillSelection(gap.skill);
        addedSomething = true;
      }
    });

    // Check projects
    committedProjects.forEach(proj => {
      // Use a simple keyword check since titles might be long
      const keywords = proj.title.toLowerCase().split(' ').filter(w => w.length > 3);
      const isMatch = lowerInput.includes(proj.title.toLowerCase()) || keywords.some(k => lowerInput.includes(k));
      
      if (isMatch && !proj.committed) {
        toggleProjectCommitment(proj.title);
        addedSomething = true;
      }
    });

    if (addedSomething) {
      setInputText('');
    }
  };

  const selectedProjects = committedProjects.filter(p => p.committed);

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex flex-col h-full space-y-6 overflow-hidden"
    >
      <div className="text-center flex-shrink-0 mb-2">
        <h2 className="text-2xl font-bold text-white tracking-tight flex items-center justify-center gap-2">
          <Sparkles className="w-6 h-6 text-cyan-400" /> Build Your Roadmap
        </h2>
        <p className="text-slate-400 mt-1">Your resume is strong. Select the exact skills and projects you want to add to achieve a 100% match.</p>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 overflow-hidden pb-16">
        
        {/* Left Side: Suggestions (2 cols) */}
        <div className="lg:col-span-2 flex flex-col space-y-4 overflow-y-auto pr-2 custom-scrollbar">
          
          {/* Missing Skills */}
          <div className="space-y-3">
            <h3 className="font-semibold text-indigo-400 flex items-center gap-2">
              <Target className="w-5 h-5" /> Missing Skills (Recommended)
            </h3>
            <div className="flex flex-wrap gap-2">
              {gaps.map((gap, idx) => {
                const isSelected = selectedSkills.includes(gap.skill);
                return (
                  <button
                    key={idx}
                    onClick={() => toggleSkillSelection(gap.skill)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-sm transition-all ${
                      isSelected 
                        ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-300 shadow-[0_0_10px_-2px_rgba(99,102,241,0.3)]' 
                        : 'bg-slate-800/50 border-slate-700/50 text-slate-300 hover:border-slate-500'
                    }`}
                  >
                    {isSelected ? <CheckCircle2 className="w-4 h-4" /> : <Plus className="w-4 h-4 text-slate-500" />}
                    {gap.skill}
                  </button>
                );
              })}
              {gaps.length === 0 && (
                <span className="text-sm text-slate-500 italic">No missing skills detected!</span>
              )}
            </div>
          </div>

          {/* Suggested Projects */}
          <div className="space-y-3 mt-6">
            <h3 className="font-semibold text-cyan-400 flex items-center gap-2">
              <Cpu className="w-5 h-5" /> Suggested Projects
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {committedProjects.map((project, idx) => (
                <div 
                  key={idx} 
                  onClick={() => toggleProjectCommitment(project.title)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer relative overflow-hidden group ${
                    project.committed 
                      ? 'bg-cyan-500/10 border-cyan-400/50' 
                      : 'bg-slate-800/40 border-slate-700 hover:border-slate-500'
                  }`}
                >
                  <div className="flex justify-between items-start mb-1 gap-2">
                    <h4 className={`font-medium text-sm leading-tight ${project.committed ? 'text-cyan-300' : 'text-slate-200'}`}>
                      {project.title}
                    </h4>
                    <div className={`flex-shrink-0 w-5 h-5 rounded border flex items-center justify-center ${
                      project.committed ? 'bg-cyan-500 border-cyan-400 text-slate-900' : 'border-slate-500'
                    }`}>
                      {project.committed && <CheckCircle2 className="w-4 h-4" />}
                    </div>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2 mt-2">{project.description}</p>
                </div>
              ))}
              {committedProjects.length === 0 && (
                <span className="text-sm text-slate-500 italic">No project suggestions needed.</span>
              )}
            </div>
          </div>
          
        </div>

        {/* Right Side: Cart (1 col) */}
        <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-5 flex flex-col h-full shadow-inner">
          <div className="flex justify-between items-center mb-4 border-b border-slate-700/50 pb-3">
            <h3 className="font-bold text-white flex items-center gap-2">
              <ShoppingCart className="w-5 h-5 text-emerald-400" /> Your Cart
            </h3>
            <span className="bg-slate-900 text-xs px-2 py-1 rounded text-slate-400 font-medium border border-slate-700">
              {selectedSkills.length + selectedProjects.length} Items
            </span>
          </div>

          <div className="flex-1 overflow-y-auto space-y-4 pr-1 custom-scrollbar">
            
            {/* Cart Skills */}
            {selectedSkills.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Added Skills</div>
                <ul className="space-y-2">
                  <AnimatePresence>
                    {selectedSkills.map(skill => (
                      <motion.li 
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        key={skill} 
                        className="flex items-center justify-between bg-slate-900/50 px-3 py-2 rounded-lg border border-slate-700 text-sm text-indigo-200"
                      >
                        {skill}
                        <button onClick={() => toggleSkillSelection(skill)} className="text-slate-500 hover:text-red-400 transition-colors">
                          <X className="w-4 h-4" />
                        </button>
                      </motion.li>
                    ))}
                  </AnimatePresence>
                </ul>
              </div>
            )}

            {/* Cart Projects */}
            {selectedProjects.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Added Projects</div>
                <ul className="space-y-2">
                  <AnimatePresence>
                    {selectedProjects.map(proj => (
                      <motion.li 
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        key={proj.title} 
                        className="flex items-center justify-between bg-slate-900/50 px-3 py-2 rounded-lg border border-slate-700 text-sm text-cyan-200"
                      >
                        <span className="truncate pr-2">{proj.title}</span>
                        <button onClick={() => toggleProjectCommitment(proj.title)} className="text-slate-500 hover:text-red-400 transition-colors flex-shrink-0">
                          <X className="w-4 h-4" />
                        </button>
                      </motion.li>
                    ))}
                  </AnimatePresence>
                </ul>
              </div>
            )}

            {selectedSkills.length === 0 && selectedProjects.length === 0 && (
              <div className="flex flex-col items-center justify-center h-40 text-slate-500 space-y-3">
                <ShoppingCart className="w-8 h-8 opacity-20" />
                <span className="text-sm">Your cart is empty</span>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Action Bar (Fixed at bottom) */}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-slate-900/90 backdrop-blur-md border-t border-slate-800 flex justify-between items-center z-10 rounded-b-2xl">
        
        {/* Natural Language Input */}
        <div className="flex-1 max-w-xl mr-4 flex items-center relative group">
          <input 
            type="text" 
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleParseInput()}
            placeholder="Type 'Add Burpsuite and Web Vul Scanner...'"
            className="w-full bg-slate-800/80 border border-slate-700 group-hover:border-slate-500 rounded-full pl-4 pr-12 py-2 text-sm text-slate-200 outline-none focus:ring-2 ring-indigo-500/50 transition-all placeholder:text-slate-500"
          />
          <button 
            onClick={handleParseInput}
            disabled={!inputText.trim()}
            className="absolute right-1 top-1/2 -translate-y-1/2 p-1.5 bg-indigo-500 text-white rounded-full disabled:opacity-50 disabled:bg-slate-700 transition-all"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center gap-3">
          <button onClick={prevStep} className="px-5 py-2.5 text-slate-400 hover:text-white rounded-lg font-medium flex items-center gap-2 transition-colors">
            <ChevronLeft className="w-4 h-4" /> Back
          </button>
          <button 
            onClick={nextStep} 
            className="px-6 py-2.5 bg-gradient-to-r from-indigo-500 to-cyan-500 hover:from-indigo-400 hover:to-cyan-400 text-white rounded-lg font-medium flex items-center gap-2 transition-transform hover:scale-[1.02] active:scale-95 shadow-[0_0_15px_-3px_rgba(99,102,241,0.5)]"
          >
            Generate Roadmap <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}

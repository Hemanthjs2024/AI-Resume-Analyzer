import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, AlertTriangle, Target, CheckCircle2, ChevronRight, Cpu, RefreshCcw } from 'lucide-react';
import useAppStore from '../store/useAppStore';

export default function AnalyseStep() {
  const { isLoading, analysisResult, nextStep, toggleProjectCommitment, committedProjects, resetApp, selectedSkills, toggleSkillSelection } = useAppStore();
  const [showThankYou, setShowThankYou] = useState(false);

  if (isLoading || !analysisResult) {
    return (
      <div className="flex flex-col items-center justify-center flex-1 h-full min-h-[400px] space-y-8">
        <div className="relative">
          <div className="w-24 h-24 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <Cpu className="w-8 h-8 text-cyan-400 animate-pulse" />
          </div>
        </div>
        <div className="text-center space-y-2">
          <h3 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">
            Deep Analyzing Your Profile
          </h3>
          <p className="text-slate-400 max-w-sm">Running skill graph traversal, NLP gap detection, and LLM optimizations...</p>
        </div>
      </div>
    );
  }

  if (showThankYou) {
    return (
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex flex-col items-center justify-center flex-1 h-full min-h-[400px] space-y-6 text-center"
      >
        <div className="w-20 h-20 bg-green-500/10 rounded-full flex items-center justify-center border border-green-500/20 mb-4">
          <CheckCircle2 className="w-10 h-10 text-green-400" />
        </div>
        <h2 className="text-3xl font-bold text-white">Thank You, Visit Again!</h2>
        <p className="text-slate-400 max-w-md">
          Your resume is already highly optimized. We're glad we could confirm that you're an excellent fit for the role.
        </p>
        <button
          onClick={resetApp}
          className="mt-8 px-6 py-2.5 bg-slate-800 text-white rounded-lg font-medium flex items-center gap-2 hover:bg-slate-700 transition-colors border border-slate-700"
        >
          <RefreshCcw className="w-4 h-4" /> Start Over
        </button>
      </motion.div>
    );
  }

  const { gap_analysis, score, candidate_name } = analysisResult;
  // Lowered threshold to 70 (Grade B or above) so it triggers more easily for a "positive" score
  const isHighlyOptimized = score.overall_score >= 70 || score.grade === 'A' || score.grade === 'B';

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col h-full space-y-6 overflow-y-auto pr-2 pb-16"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className="text-2xl font-bold text-white mb-1">Analysis Complete</h2>
          <p className="text-slate-400">
            Hi <span className="text-cyan-400 font-semibold">{candidate_name}</span>, 
            {isHighlyOptimized 
              ? ` your resume is already highly optimized! Excellent match.` 
              : ` here is your skill gap breakdown.`}
          </p>
        </div>
      </div>

      <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 p-6 mb-6">
        <div className="flex flex-col md:flex-row justify-between gap-8">
          {/* Overall Score Circle */}
          <div className="flex flex-col items-center justify-center space-y-2 pr-8 md:border-r border-slate-700 min-w-[140px]">
            <div className="relative w-24 h-24 flex items-center justify-center">
              <svg className="w-24 h-24 transform -rotate-90">
                <circle cx="48" cy="48" r="42" fill="transparent" stroke="rgba(30, 41, 59, 0.8)" strokeWidth="6" />
                <circle cx="48" cy="48" r="42" fill="transparent" 
                  stroke="currentColor" 
                  className={`${score.grade === 'A' ? 'text-green-400' : score.grade === 'B' ? 'text-blue-400' : score.grade === 'C' ? 'text-yellow-400' : 'text-red-400'}`}
                  strokeWidth="6" 
                  strokeDasharray={263.8} 
                  strokeDashoffset={263.8 - (263.8 * score.overall_score) / 100} 
                  strokeLinecap="round" 
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-2xl font-bold text-white">{score.overall_score}</span>
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Grade {score.grade}</span>
              </div>
            </div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Initial Score</div>
          </div>

          {/* Breakdown Grid */}
          <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="space-y-2">
              <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Keyword Match</div>
              <div className="text-xl font-bold text-indigo-400">{score.breakdown.keyword_match}%</div>
              <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                <div className="bg-indigo-500 h-full" style={{ width: `${score.breakdown.keyword_match}%` }}></div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Impact Score</div>
              <div className="text-xl font-bold text-cyan-400">{score.breakdown.impact_score}%</div>
              <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                <div className="bg-cyan-500 h-full" style={{ width: `${score.breakdown.impact_score}%` }}></div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Formatting</div>
              <div className="text-xl font-bold text-emerald-400">{score.breakdown.format_score}%</div>
              <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full" style={{ width: `${score.breakdown.format_score}%` }}></div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Completeness</div>
              <div className="text-xl font-bold text-amber-400">{score.breakdown.completeness_score}%</div>
              <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                <div className="bg-amber-500 h-full" style={{ width: `${score.breakdown.completeness_score}%` }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Alignment Insights */}
      {score?.ai_analysis && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-indigo-500/5 rounded-2xl border border-indigo-500/20 p-6 mb-6"
        >
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center flex-shrink-0 border border-indigo-500/30">
              <Cpu className="w-7 h-7 text-indigo-400" />
            </div>
            <div className="space-y-3">
              <div>
                <h4 className="text-sm font-bold text-indigo-300 uppercase tracking-widest flex items-center gap-2">
                  Strategic AI Insights
                  <span className="px-2 py-0.5 rounded text-[10px] bg-indigo-500/20 text-indigo-400 border border-indigo-500/20">AI Driven</span>
                </h4>
                <p className="text-slate-300 text-sm mt-2 leading-relaxed">
                  {score.ai_analysis.reasoning}
                </p>
              </div>
              
              {score.ai_analysis.feedback?.strategic_advice && (
                <div className="bg-slate-900/60 rounded-xl p-4 border border-indigo-500/20 relative overflow-hidden group">
                  <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>
                  <div className="text-[10px] text-slate-500 uppercase font-bold mb-1 tracking-wider">Top Strategic Recommendation</div>
                  <div className="text-xs text-indigo-300 font-medium italic">
                    "{score.ai_analysis.feedback.strategic_advice}"
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Target Skill Set (JD Keywords) */}
      <div className="bg-slate-900/50 rounded-2xl border border-slate-700/50 p-6 space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-indigo-400" /> Target Skill Set (JD Keywords)
          </h3>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Selected: {selectedSkills.length}</span>
            <div className="h-4 w-px bg-slate-700 mx-1"></div>
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Weight: 35%</span>
          </div>
        </div>
        
        <div className="flex flex-wrap gap-2">
          {(score?.details?.keyword_match?.matched || []).map((skill, i) => (
            <div key={`m-${i}`} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-green-500/10 border border-green-500/20 text-xs text-green-300">
              <CheckCircle2 className="w-3.5 h-3.5" /> {skill}
            </div>
          ))}
          {(score?.details?.keyword_match?.missing || []).map((skill, i) => {
            const isSelected = selectedSkills.includes(skill);
            return (
              <button 
                key={`ms-${i}`} 
                onClick={() => toggleSkillSelection(skill)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs transition-all ${
                  isSelected 
                    ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-300 shadow-[0_0_10px_-2px_rgba(99,102,241,0.3)]' 
                    : 'bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-500'
                }`}
              >
                {isSelected ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5 text-amber-500/60" />}
                {skill}
              </button>
            );
          })}
        </div>
        
        <p className="text-xs text-slate-500 italic">
          Tip: <span className="text-indigo-400 font-medium font-sans">Click on missing skills above</span> to add them to your resume and increase your match weight.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gap Analysis Column */}
        <div className="flex flex-col h-[500px]">
          <div className="flex items-center gap-2 mb-4 text-indigo-400 font-semibold flex-shrink-0">
            <Target className="w-5 h-5" /> Gap Analysis via Skill Graph
          </div>
          
          <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 overflow-y-auto flex-1 custom-scrollbar">
            {(gap_analysis?.gaps || []).map((gap, idx) => (
              <div key={idx} className="p-4 border-b border-slate-700/50 last:border-0 hover:bg-slate-800/80 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <div className="font-semibold text-slate-200">{gap.skill}</div>
                  {gap.reachable ? (
                    <span className="px-2 py-1 text-xs rounded-md bg-green-500/10 text-green-400 border border-green-500/20">
                      Reachable
                    </span>
                  ) : (
                    <span className="px-2 py-1 text-xs rounded-md bg-red-500/10 text-red-400 border border-red-500/20">
                      Gap Too Large
                    </span>
                  )}
                </div>
                
                {gap.reachable ? (
                  <div className="text-sm text-slate-400 space-y-1">
                    <div className="flex flex-wrap items-center gap-1">
                      Path: 
                      {(gap?.path || []).map((node, i) => (
                        <React.Fragment key={i}>
                          <span className={`${i === gap.path.length-1 ? 'text-cyan-400 font-medium' : 'text-slate-300'}`}>{node}</span>
                          {i < gap.path.length - 1 && <ChevronRight className="w-3 h-3 text-slate-600" />}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-sm text-red-400/80 flex items-start gap-1.5">
                    <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    No logical path found from your current skills. Consider lower-level roles first.
                  </div>
                )}
              </div>
            ))}
            {gap_analysis.gaps.length === 0 && (
              <div className="p-8 text-center text-slate-400">
                <CheckCircle2 className="w-8 h-8 text-green-400 mx-auto mb-2" />
                No skill gaps found! You are a perfect technical match.
              </div>
            )}
          </div>
        </div>

        {/* Project Suggestions Column */}
        <div className="flex flex-col h-[500px]">
          <div className="flex items-center gap-2 mb-4 text-cyan-400 font-semibold flex-shrink-0">
            <Cpu className="w-5 h-5" /> Suggested Projects to Bridge Gaps
          </div>
          
          <div className="overflow-y-auto flex-1 pr-2 custom-scrollbar space-y-4">
            {(committedProjects || []).map((project, idx) => (
              <div 
                key={idx} 
                className={`p-5 rounded-xl border transition-all cursor-pointer ${
                  project.committed 
                    ? 'bg-cyan-500/10 border-cyan-400/50 shadow-[0_0_15px_-3px_rgba(34,211,238,0.2)]' 
                    : 'bg-slate-800/50 border-slate-700 hover:border-slate-500'
                }`}
                onClick={() => toggleProjectCommitment(project.title)}
              >
                <div className="flex justify-between items-start mb-2 gap-4">
                  <h4 className={`font-semibold ${project.committed ? 'text-cyan-300' : 'text-slate-200'}`}>
                    {project.title}
                  </h4>
                  <div className="flex-shrink-0">
                    <div className={`w-5 h-5 rounded border flex items-center justify-center ${
                      project.committed ? 'bg-cyan-500 border-cyan-400 text-slate-900' : 'border-slate-500'
                    }`}>
                      {project.committed && <CheckCircle2 className="w-4 h-4" />}
                    </div>
                  </div>
                </div>
                
                <p className="text-sm text-slate-400 mb-3">{project.description}</p>
                
                <div className="flex flex-wrap gap-2 mb-3">
                  {(project?.tech_stack || []).map((tech, i) => (
                    <span key={i} className="px-2 py-0.5 text-xs bg-slate-700/50 text-slate-300 rounded">
                      {tech}
                    </span>
                  ))}
                </div>
                
                <div className="flex items-center gap-4 text-xs text-slate-500">
                  <span>⏱ {project.estimated_time}</span>
                  <span>🎯 Bridges: <span className="text-indigo-400 font-medium">{project.target_skill}</span></span>
                </div>
              </div>
            ))}
            
            {committedProjects.length === 0 && (
              <div className="p-8 text-center text-slate-500 border border-dashed border-slate-700 rounded-xl">
                No reachable projects needed for this role.
              </div>
            )}
          </div>
          
          {committedProjects.length > 0 && (
            <p className="text-xs text-slate-500 text-center uppercase tracking-wide mt-2">
              Select projects you commit to building. They will be added to your generated resume and roadmap.
            </p>
          )}
        </div>
      </div>

      {/* Action Bar (Fixed at bottom) */}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-slate-900/80 backdrop-blur border-t border-slate-800 flex justify-between items-center z-10 rounded-b-2xl">
        <div className="text-sm text-slate-400">
          <span className="text-white font-medium">{committedProjects.filter(p => p.committed).length}</span> projects committed
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={resetApp}
            className="px-5 py-2.5 text-slate-400 hover:text-white transition-colors font-medium"
          >
            Reset
          </button>
          <button
            onClick={nextStep}
            className="px-6 py-2.5 bg-gradient-to-r from-indigo-500 to-cyan-500 hover:from-indigo-400 hover:to-cyan-400 text-white rounded-lg font-medium flex items-center gap-2 transition-transform hover:scale-[1.02] active:scale-95 shadow-lg shadow-indigo-500/20"
          >
            Review Resume Content <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}

import { motion } from 'framer-motion';
import { FileDown, FileText, CheckCircle2, AlertCircle, Loader2, ChevronRight } from 'lucide-react';
import useAppStore from '../store/useAppStore';
import { getDownloadUrl, generateRoadmap } from '../api/client';

export default function ScoreDownloadStep() {
  const { analysisResult, generatedFiles, committedProjects, selectedSkills, setRoadmap } = useAppStore();

  const handleDownload = async (filename) => {
    // 1. Trigger the download via browser
    window.open(getDownloadUrl(filename), '_blank');

    // 2. If they have committed projects, generate and show roadmap popup
    const committed = committedProjects.filter(p => p.committed);
    if (committed.length > 0) {
      try {
        // If user manually selected skills in the Suggestion Cart, only pass those. Otherwise pass all.
        const allGaps = analysisResult?.gap_analysis?.gaps || [];
        const filteredGaps = selectedSkills.length > 0 
          ? allGaps.filter(g => selectedSkills.includes(g.skill))
          : allGaps;

        const roadmapData = await generateRoadmap(committed, filteredGaps);
        setRoadmap(roadmapData);
      } catch (e) {
        console.error("Failed to generate roadmap", e);
      }
    }
  };

  if (!analysisResult || !generatedFiles || !analysisResult.score) return (
    <div className="flex flex-col items-center justify-center h-full space-y-4 text-slate-400">
      <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      <p>Finalizing your results...</p>
    </div>
  );

  const { score } = analysisResult;
  
  // Calculate Improved Score
  const originalScore = score.overall_score || 0;
  const skillBonus = Math.min((selectedSkills || []).length * 3, 15);
  const projectBonus = Math.min((committedProjects || []).filter(p => p.committed).length * 7, 21);
  const sectionBonus = 10;
  const improvedScore = Math.min(originalScore + skillBonus + projectBonus + sectionBonus, 100);

  const getGrade = (s) => {
    if (s >= 90) return 'A';
    if (s >= 80) return 'B';
    if (s >= 70) return 'C';
    return 'D';
  };

  const improvedGrade = getGrade(improvedScore);

  const gradeColors = {
    'A': 'text-green-400 drop-shadow-[0_0_15px_rgba(74,222,128,0.5)]',
    'B': 'text-blue-400 drop-shadow-[0_0_15px_rgba(96,165,250,0.5)]',
    'C': 'text-yellow-400 drop-shadow-[0_0_15px_rgba(250,204,21,0.5)]',
    'D': 'text-red-400 drop-shadow-[0_0_15px_rgba(248,113,113,0.5)]'
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col h-full space-y-6 overflow-y-auto pr-2"
    >
      <div className="text-center space-y-2 mb-4">
        <h2 className="text-3xl font-bold text-white tracking-tight">Your Resume is Ready</h2>
        <p className="text-slate-400">Download the ATS-optimized file below.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
        {/* Score Column */}
        <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 p-6 flex flex-col items-center">
          
          <div className="flex gap-8 mb-6">
             {/* Original Score */}
             <div className="flex flex-col items-center opacity-40 scale-90">
               <div className="relative w-28 h-28 flex items-center justify-center">
                 <svg className="w-28 h-28 transform -rotate-90">
                   <circle cx="56" cy="56" r="48" fill="transparent" stroke="rgba(30, 41, 59, 0.8)" strokeWidth="6" />
                   <circle cx="56" cy="56" r="48" fill="transparent" 
                     stroke="currentColor" 
                     className={`${score.grade === 'A' ? 'text-green-400' : score.grade === 'B' ? 'text-blue-400' : score.grade === 'C' ? 'text-yellow-400' : 'text-red-400'}`}
                     strokeWidth="6" 
                     strokeDasharray={301.6} 
                     strokeDashoffset={301.6 - (301.6 * originalScore) / 100} 
                   />
                 </svg>
                 <span className="absolute text-xl font-bold text-white">{originalScore}</span>
               </div>
               <span className="text-[10px] text-slate-500 uppercase tracking-widest mt-2">Original</span>
             </div>

             <div className="flex items-center text-slate-600">
               <ChevronRight className="w-8 h-8" />
             </div>

             {/* Improved Score */}
             <div className="flex flex-col items-center">
               <div className="relative w-32 h-32 flex items-center justify-center">
                 <motion.div 
                   initial={{ scale: 0.8, opacity: 0 }}
                   animate={{ scale: 1, opacity: 1 }}
                   transition={{ delay: 0.3 }}
                   className="absolute inset-0 bg-indigo-500/10 rounded-full blur-xl"
                 ></motion.div>
                 <svg className="w-32 h-32 transform -rotate-90">
                   <circle cx="64" cy="64" r="56" fill="transparent" stroke="rgba(30, 41, 59, 0.8)" strokeWidth="10" />
                   <motion.circle 
                     initial={{ strokeDashoffset: 351.8 }}
                     animate={{ strokeDashoffset: 351.8 - (351.8 * improvedScore) / 100 }}
                     transition={{ duration: 1.5, delay: 0.5 }}
                     cx="64" cy="64" r="56" fill="transparent" 
                     stroke="currentColor" 
                     className={`${improvedGrade === 'A' ? 'text-green-400' : improvedGrade === 'B' ? 'text-blue-400' : improvedGrade === 'C' ? 'text-yellow-400' : 'text-red-400'}`}
                     strokeWidth="10" 
                     strokeDasharray={351.8} 
                     strokeLinecap="round" 
                   />
                 </svg>
                 <div className="absolute flex flex-col items-center">
                   <span className={`text-3xl font-bold ${gradeColors[improvedGrade]}`}>{improvedScore}</span>
                   <span className="text-[10px] text-slate-400 uppercase tracking-widest">Grade {improvedGrade}</span>
                 </div>
               </div>
               <span className="text-[10px] text-indigo-400 font-bold uppercase tracking-widest mt-2">Improved</span>
             </div>
          </div>

          <div className="w-full space-y-4">
            <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-widest border-b border-slate-700 pb-2 flex justify-between">
              <span>Improvement Match</span>
              <span className="text-indigo-400">+{improvedScore - originalScore} Points</span>
            </h4>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Added Projects Impact</span>
                <span className="text-cyan-400 font-medium">+{projectBonus}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Skill Gap Closure</span>
                <span className="text-indigo-400 font-medium">+{skillBonus}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Section Optimization</span>
                <span className="text-emerald-400 font-medium">+{sectionBonus}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Action Column */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 border border-indigo-500/30 rounded-2xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">Download Resume</h3>
            
            <div className="space-y-3">
              <button 
                onClick={() => handleDownload(generatedFiles.docx_filename)}
                className="w-full flex items-center justify-between px-5 py-4 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-xl transition-all group"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg"><FileText className="w-5 h-5"/></div>
                  <div className="text-left">
                    <div className="font-semibold text-slate-200 group-hover:text-white">Word Document (.docx)</div>
                    <div className="text-xs text-slate-400">Best for ATS systems</div>
                  </div>
                </div>
                <FileDown className="w-5 h-5 text-slate-500 group-hover:text-blue-400" />
              </button>

              {generatedFiles.pdf_available && (
                <button 
                  onClick={() => handleDownload(generatedFiles.pdf_filename)}
                  className="w-full flex items-center justify-between px-5 py-4 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-xl transition-all group"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-red-500/10 text-red-500 rounded-lg"><FileText className="w-5 h-5"/></div>
                    <div className="text-left">
                      <div className="font-semibold text-slate-200 group-hover:text-white">PDF Document (.pdf)</div>
                      <div className="text-xs text-slate-400">Best for emails / humans</div>
                    </div>
                  </div>
                  <FileDown className="w-5 h-5 text-slate-500 group-hover:text-red-400" />
                </button>
              )}
            </div>
          </div>

          <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 p-6">
            <h4 className="font-medium text-slate-200 mb-3 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-400" /> 
              Remaining Issues
            </h4>
            {score.all_issues.length > 0 ? (
              <ul className="space-y-2">
                {score.all_issues.map((issue, i) => (
                  <li key={i} className="text-sm text-slate-400 flex items-start gap-2">
                    <span className="text-slate-600 mt-1">•</span> {issue}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-green-400 flex items-center gap-2"><CheckCircle2 className="w-4 h-4"/> Looks perfect!</p>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

import { motion, AnimatePresence } from 'framer-motion';
import { X, Calendar, BookOpen, ExternalLink, Lightbulb, User } from 'lucide-react';
import useAppStore from '../store/useAppStore';

export default function RoadmapPopup() {
  const { roadmap, setRoadmap } = useAppStore();

  if (!roadmap) return null;

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/80 backdrop-blur-md"
      >
        <motion.div 
          initial={{ scale: 0.95, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.95, opacity: 0, y: 20 }}
          className="bg-slate-800 w-full max-w-4xl max-h-[90vh] rounded-2xl border border-slate-700/50 shadow-2xl flex flex-col overflow-hidden relative"
        >
          {/* Header */}
          <div className="p-6 border-b border-slate-700 flex justify-between items-start bg-slate-800/80 sticky top-0 z-10">
            <div>
              <div className="flex items-center gap-2 text-cyan-400 font-medium mb-1 tracking-wide uppercase text-xs">
                <Calendar className="w-4 h-4" /> Personalized Career Plan
              </div>
              <h2 className="text-2xl font-bold text-white">Your {roadmap.estimated_duration} Roadmap to {roadmap.target_skill}</h2>
              <p className="text-slate-400 mt-1 flex items-center gap-2">
                <User className="w-4 h-4" /> Based on your current level ({roadmap.user_level}) to build: <strong className="text-slate-300">{roadmap.project_title}</strong>
              </p>
            </div>
            <button 
              onClick={() => setRoadmap(null)}
              className="p-2 rounded-lg bg-slate-700/50 text-slate-400 hover:text-white hover:bg-slate-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Body */}
          <div className="flex-1 overflow-y-auto p-6 space-y-8">
            
            {/* Warning Banner */}
            <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 flex gap-3 text-amber-200 text-sm leading-relaxed">
              <Lightbulb className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
              <div>{roadmap.interview_warning}</div>
            </div>

            {/* Weeks */}
            <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-700 before:to-transparent">
              {roadmap.weeks.map((week, idx) => (
                <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                  {/* Timeline Dot */}
                  <div className="flex items-center justify-center w-10 h-10 rounded-full border border-slate-700 bg-slate-800 text-cyan-400 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 font-bold">
                    {week.week}
                  </div>
                  
                  {/* Content Card */}
                  <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-slate-900/50 p-5 rounded-xl border border-slate-700/50 shadow-lg">
                    <h3 className="font-bold text-lg text-slate-200 mb-3">{week.theme}</h3>
                    
                    <div className="space-y-4">
                      {/* Tasks */}
                      <div>
                        <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Key Tasks</h4>
                        <ul className="space-y-1.5">
                          {week.tasks.map((task, i) => (
                            <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                              <span className="text-indigo-400 mt-1 text-xs">•</span> {task}
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Resources */}
                      {week.resources && week.resources.length > 0 && (
                        <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/50">
                          <h4 className="text-xs font-semibold text-slate-500 uppercase flex items-center gap-1.5 mb-2">
                            <BookOpen className="w-3.5 h-3.5" /> Curated Resources
                          </h4>
                          <div className="flex flex-col gap-2 relative z-20">
                            {week.resources.map((res, i) => (
                              <a 
                                key={i} 
                                href={res.url} 
                                target="_blank" 
                                rel="noreferrer"
                                className="text-sm text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5"
                              >
                                {res.title} <ExternalLink className="w-3 h-3 flex-shrink-0" />
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {/* Deliverable */}
                      <div className="text-sm bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 px-3 py-2 rounded-lg font-medium">
                        <span className="opacity-70">Goal:</span> {week.deliverable}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Interview Tips Section */}
            {roadmap.interview_tips && (
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
                <h3 className="font-bold text-lg text-slate-200 mb-4 flex items-center gap-2">
                  <User className="w-5 h-5 text-indigo-400" /> General Interview Tips for this Project
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {roadmap.interview_tips.map((tip, i) => (
                    <div key={i} className="text-sm text-slate-300 flex items-start gap-2 bg-slate-900/30 p-3 rounded-lg">
                      <span className="text-indigo-500 mt-0.5 text-lg leading-none">•</span> {tip}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

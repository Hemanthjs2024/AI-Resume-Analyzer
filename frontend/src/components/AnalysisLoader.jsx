import React from 'react';
import { motion } from 'framer-motion';
import { Cpu } from 'lucide-react';

export default function AnalysisLoader() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/80 backdrop-blur-md"
    >
      <div className="flex flex-col items-center justify-center space-y-8">
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
          <p className="text-slate-400 max-w-sm">
            Running skill graph traversal, NLP gap detection, and LLM optimizations...
          </p>
        </div>
      </div>
    </motion.div>
  );
}

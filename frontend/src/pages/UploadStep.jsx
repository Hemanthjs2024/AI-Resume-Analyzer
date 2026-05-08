import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileText, ChevronRight, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import useAppStore from '../store/useAppStore';
import { analyzeResume } from '../api/client';

export default function UploadStep() {
  const { setResumeFile, setJdText, jdText, resumeFile, nextStep, setAnalysisResult, setIsLoading, isLoading } = useAppStore();
  const [error, setError] = useState('');

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      if (file.type === 'application/pdf' || file.name.endsWith('.docx') || file.name.endsWith('.doc')) {
        setResumeFile(file);
        setError('');
      } else {
        setError('Please upload a PDF or DOCX file.');
      }
    }
  }, [setResumeFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc']
    },
    maxFiles: 1
  });

  const handleAnalyse = async () => {
    if (!resumeFile) return setError('Resume file is required.');
    if (!jdText.trim()) return setError('Job description is required.');
    
    setError('');
    setIsLoading(true);
    
    try {
      const result = await analyzeResume(resumeFile, jdText);
      setAnalysisResult(result);
      nextStep();
      
      // Initialize review items from the optimized sections map
      if (result.review_items) {
        useAppStore.getState().setReviewItems(result.review_items);
      }
      if (result.project_suggestions) {
        useAppStore.getState().setCommittedProjects(result.project_suggestions);
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to analyze. Please ensure backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex flex-col h-full space-y-6"
    >
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold text-white tracking-tight">Let's Align Your Career</h2>
        <p className="text-slate-400 max-w-2xl mx-auto">Upload your current resume and the target job description. Our AI will analyze the gaps and build a roadmap to get you there.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-1 mt-6">
        {/* Upload Column */}
        <div className="flex flex-col">
          <label className="text-sm font-medium text-slate-300 mb-2 flex items-center gap-2">
            <FileText className="w-4 h-4 text-indigo-400" />
            Resume (PDF/DOCX)
          </label>
          <div 
            {...getRootProps()} 
            className={`flex-1 border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-8 transition-all cursor-pointer bg-slate-800/30 ${
              isDragActive ? 'border-indigo-400 bg-indigo-500/10' : 
              resumeFile ? 'border-cyan-500/50 bg-cyan-500/5' : 'border-slate-600 hover:border-slate-500 hover:bg-slate-800/50'
            }`}
          >
            <input {...getInputProps()} />
            {resumeFile ? (
              <div className="flex flex-col items-center text-center space-y-3">
                <div className="w-16 h-16 rounded-full bg-cyan-500/20 flex items-center justify-center">
                  <FileText className="w-8 h-8 text-cyan-400" />
                </div>
                <div>
                  <p className="font-semibold text-slate-200">{resumeFile.name}</p>
                  <p className="text-xs text-slate-400 mt-1">{(resumeFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <p className="text-xs text-indigo-400 mt-2">Click or drag to replace</p>
              </div>
            ) : (
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="w-16 h-16 rounded-full bg-slate-700 flex items-center justify-center mb-2 group-hover:bg-slate-600 transition-colors">
                  <UploadCloud className="w-8 h-8 text-slate-400" />
                </div>
                <div>
                  <p className="font-medium text-slate-300">Drag & drop your resume</p>
                  <p className="text-sm text-slate-500 mt-1">or click to browse files</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* JD Column */}
        <div className="flex flex-col">
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              Target Job Description
            </label>
            <span className="text-xs text-slate-500">{jdText.length} chars</span>
          </div>
          <textarea
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            placeholder="Paste the full job description here..."
            className="flex-1 w-full bg-slate-800/50 border border-slate-600 rounded-xl p-4 text-sm text-slate-200 placeholder:text-slate-500 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none resize-none transition-all"
          />
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm text-center">
          {error}
        </div>
      )}

      {/* Action Bar */}
      <div className="pt-4 flex justify-end border-t border-slate-700/50">
        <button
          onClick={handleAnalyse}
          disabled={!resumeFile || !jdText.trim() || isLoading}
          className="px-8 py-3 bg-gradient-to-r from-indigo-500 to-cyan-500 hover:from-indigo-400 hover:to-cyan-400 text-white rounded-lg font-medium flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40"
        >
          {isLoading ? (
            <><Loader2 className="w-5 h-5 animate-spin" /> Analyzing...</>
          ) : (
            <>Analyse Career Fit <ChevronRight className="w-5 h-5" /></>
          )}
        </button>
      </div>
    </motion.div>
  );
}

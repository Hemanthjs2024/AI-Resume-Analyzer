import React from 'react';
import useAppStore from './store/useAppStore';
import StepIndicator from './components/StepIndicator';
import UploadStep from './pages/UploadStep';
import AnalyseStep from './pages/AnalyseStep';
import ReviewStep from './pages/ReviewStep';
import GenerateStep from './pages/GenerateStep';
import ScoreDownloadStep from './pages/ScoreDownloadStep';
import SuggestionCartStep from './pages/SuggestionCartStep';
import RoadmapPopup from './components/RoadmapPopup';
import ChatAssistant from './components/ChatAssistant';

function App() {
  const currentStep = useAppStore(state => state.currentStep);
  const roadmap = useAppStore(state => state.roadmap);
  const analysisResult = useAppStore(state => state.analysisResult);

  // Scroll to top on step change
  React.useEffect(() => {
    window.scrollTo(0, 0);
  }, [currentStep]);
  
  const isHighlyOptimized = analysisResult?.score?.overall_score >= 70 || analysisResult?.score?.grade === 'A' || analysisResult?.score?.grade === 'B';
  
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans relative">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-400 flex items-center justify-center font-bold text-white shadow-lg">
              AI
            </div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400">
              Career Alignment Agent
            </h1>
          </div>
          <StepIndicator />
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-6xl mx-auto p-4 md:p-8 flex flex-col relative">
        <div className="w-full bg-slate-800/40 rounded-2xl border border-slate-700/50 shadow-2xl overflow-hidden glass-panel flex-1 flex flex-col relative z-10 p-6">
          {currentStep === 1 && <UploadStep />}
          {currentStep === 2 && <AnalyseStep />}
          {currentStep === 3 && (isHighlyOptimized ? <SuggestionCartStep /> : <ReviewStep />)}
          {currentStep === 4 && <GenerateStep />}
          {currentStep === 5 && <ScoreDownloadStep />}
        </div>
      </main>

      {/* Floating Elements */}
      <ChatAssistant />
      
      {/* Fullscreen Overlays */}
      {roadmap && <RoadmapPopup />}
      
      {/* Abstract Background Decoration */}
      <div className="fixed top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-900/20 blur-[120px] pointer-events-none z-0"></div>
      <div className="fixed bottom-[-20%] right-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-900/20 blur-[120px] pointer-events-none z-0"></div>
    </div>
  );
}

export default App;

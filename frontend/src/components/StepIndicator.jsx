import { Fragment } from 'react';
import useAppStore from '../store/useAppStore';
import { CheckCircle2 } from 'lucide-react';

const STEPS = [
  { id: 1, label: 'Upload' },
  { id: 2, label: 'Analyse' },
  { id: 3, label: 'Review' },
  { id: 4, label: 'Generate' },
  { id: 5, label: 'Score' },
];

export default function StepIndicator() {
  const currentStep = useAppStore(state => state.currentStep);

  return (
    <div className="hidden md:flex items-center gap-2 text-sm font-medium">
      {STEPS.map((step, index) => {
        const isActive = currentStep === step.id;
        const isPast = currentStep > step.id;
        
        return (
          <Fragment key={step.id}>
            <div className={`flex items-center gap-1.5 transition-colors duration-300 ${
              isActive ? 'text-cyan-400' : isPast ? 'text-indigo-400' : 'text-slate-500'
            }`}>
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs border ${
                isActive ? 'border-cyan-400 bg-cyan-400/10' : 
                isPast ? 'border-indigo-400 bg-indigo-400/10' : 
                'border-slate-600 bg-transparent'
              }`}>
                {isPast ? <CheckCircle2 className="w-4 h-4" /> : step.id}
              </div>
              <span className={isActive ? 'text-slate-200' : ''}>{step.label}</span>
            </div>
            {index < STEPS.length - 1 && (
              <div className={`w-6 h-[1px] ${isPast ? 'bg-indigo-500/50' : 'bg-slate-700'}`} />
            )}
            </Fragment>
        );
      })}
    </div>
  );
}

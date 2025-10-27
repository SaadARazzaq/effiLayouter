import { Check, Clock, Play } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface WizardStepperProps {
  steps: Array<{ id: number; title: string; visibleWhen?: string }>;
  currentStep: number;
  completedSteps: number[];
  runningSteps: number[];
  selectedLanguage: string;
  onStepClick: (stepId: number) => void;
  canProceedToStep: (stepId: number) => boolean;
}

export function WizardStepper({ 
  steps, 
  currentStep, 
  completedSteps = [], 
  runningSteps = [],
  selectedLanguage,
  onStepClick,
  canProceedToStep
}: WizardStepperProps) {
  const visibleSteps = steps.filter(step => 
    !step.visibleWhen || step.visibleWhen === selectedLanguage
  );

  return (
    <div className="w-full py-8">
      <div className="relative">
        {/* Background Progress Line */}
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-muted-foreground/20 rounded-full" />
        <div 
          className="absolute top-5 left-0 h-0.5 bg-gradient-to-r from-primary to-primary/80 rounded-full transition-all duration-700 ease-out"
          style={{ 
            width: `${(completedSteps.length / visibleSteps.length) * 100}%` 
          }}
        />
        
        <div className="flex items-center justify-between max-w-4xl mx-auto px-4 relative">
          {visibleSteps.map((step, index) => {
            const isCompleted = completedSteps.includes(step.id);
            const isRunning = runningSteps.includes(step.id);
            const isCurrent = currentStep === step.id;
            const canProceed = canProceedToStep(step.id);
            const isClickable = canProceed || isCompleted;

            return (
              <div key={step.id} className="flex items-center relative">
                {/* Step Circle */}
                <div className="flex flex-col items-center group">
                  <button
                    onClick={() => isClickable && onStepClick(step.id)}
                    disabled={!isClickable}
                    className={cn(
                      "relative w-10 h-10 rounded-full border-2 flex items-center justify-center text-sm font-semibold transition-all duration-300",
                      "focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary shadow-lg",
                      isCompleted && "bg-gradient-to-br from-green-500 to-green-600 border-green-500 text-white shadow-green-500/25",
                      isRunning && "bg-gradient-to-br from-primary to-primary/80 border-primary text-primary-foreground animate-pulse",
                      isCurrent && !isCompleted && !isRunning && canProceed && "border-primary text-primary bg-primary/10 shadow-primary/20",
                      !canProceed && !isCompleted && !isRunning && "border-muted-foreground/30 text-muted-foreground bg-muted/20",
                      isClickable && "hover:scale-110 hover:shadow-xl cursor-pointer transform-gpu",
                      !isClickable && "cursor-not-allowed opacity-60"
                    )}
                    aria-label={`Step ${step.id}: ${step.title}`}
                  >
                    {/* Animated ring for current step */}
                    {isCurrent && !isCompleted && !isRunning && (
                      <div className="absolute inset-0 rounded-full border-2 border-primary animate-ping opacity-30" />
                    )}
                    
                    {isCompleted ? (
                      <Check className="w-5 h-5 animate-scale-in" />
                    ) : isRunning ? (
                      <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <span className="font-bold">{step.id}</span>
                    )}
                  </button>
                  
                  <div className="mt-3 text-center max-w-24">
                    <div className={cn(
                      "text-xs font-medium transition-all duration-300",
                      isCurrent && "text-primary font-semibold",
                      isCompleted && "text-green-600 dark:text-green-400",
                      isRunning && "text-primary",
                      !canProceed && !isCompleted && !isRunning && "text-muted-foreground"
                    )}>
                      {step.title}
                    </div>
                    
                    {/* Status indicators */}
                    {isCompleted && (
                      <div className="mt-1">
                        <Badge variant="secondary" className="text-xs px-2 py-0 bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300">
                          Done
                        </Badge>
                      </div>
                    )}
                    {isRunning && (
                      <div className="mt-1">
                        <Badge variant="secondary" className="text-xs px-2 py-0 bg-primary/10 text-primary animate-pulse">
                          Running
                        </Badge>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
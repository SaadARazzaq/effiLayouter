import { Loader2, Play, CheckCircle, AlertCircle, Clock, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { WizardStep as WizardStepType, StepExecution } from '@/types/wizard';
import { StepForm } from './StepForm';
import { StepLogs } from './StepLogs';
import { SplitView } from './SplitView';
import { cn } from '@/lib/utils';

interface WizardStepProps {
  step: WizardStepType;
  selectedLanguage: 'english' | 'arabic';
  execution?: StepExecution;
  formData: Record<string, any>;
  onFormChange: (data: Record<string, any>) => void;
  onExecute: () => void;
  onNext: () => void;
  onBack: () => void;
  canGoBack: boolean;
  canGoNext: boolean;
  canExecute: boolean;
  isLastStep: boolean;
  visibleSteps: WizardStepType[];
  completedSteps: number[];
}

export function WizardStepComponent({
  step,
  selectedLanguage,
  execution,
  formData,
  onFormChange,
  onExecute,
  onNext,
  onBack,
  canGoBack,
  canGoNext,
  canExecute,
  isLastStep,
  visibleSteps = [],
  completedSteps = []
}: WizardStepProps) {
  const isRunning = execution?.status === 'running';
  const isCompleted = execution?.status === 'success';
  const hasError = execution?.status === 'error';

  const getStepStatus = () => {
    if (hasError) return { icon: AlertCircle, label: 'Failed', variant: 'destructive' as const };
    if (isCompleted) return { icon: CheckCircle, label: 'Completed', variant: 'success' as const };
    if (isRunning) return { icon: Clock, label: 'Running', variant: 'default' as const };
    return null;
  };

  const stepStatus = getStepStatus();

  const getExecutionTime = () => {
    return execution?.logs?.length ? `${execution.logs.length} operations` : '';
  };

  // Handle special case for comparison step
  if (step.viewer) {
    const rightFile = step.viewer.rightConditional[selectedLanguage];
    
    return (
      <div className="space-y-6">
        <Card className="animate-scale-in shadow-xl border-0 bg-gradient-to-br from-card to-card/80 backdrop-blur-sm">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary/80 rounded-lg flex items-center justify-center">
                    <span className="text-primary-foreground font-bold text-sm">{step.id}</span>
                  </div>
                  <span>{step.title}</span>
                </CardTitle>
              </div>
              <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">Final Step</Badge>
            </div>
            <CardDescription>{step.desc}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[600px] w-full">
              <SplitView
                leftFile={step.viewer.left}
                rightFile={rightFile}
                leftTitle="Original PDF"
                rightTitle="Translated PDF"
                className="h-full"
              />
            </div>
            
            {step.actions && (
              <div className="mt-4 flex space-x-2">
                {step.actions.map((action, index) => (
                  <Button
                    key={index}
                    className="bg-gradient-to-r from-primary to-primary/90 hover:from-primary/90 hover:to-primary text-primary-foreground shadow-lg hover:shadow-xl transition-all duration-200"
                    onClick={() => {
                      if (action.toConditional) {
                        window.open(action.toConditional[selectedLanguage], '_blank');
                      }
                    }}
                  >
                    <ArrowRight className="w-4 h-4 mr-2" />
                    {action.label}
                  </Button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card className="animate-scale-in shadow-xl border-0 bg-gradient-to-br from-card to-card/80 backdrop-blur-sm overflow-hidden">
        {/* Progress bar at top of card */}
        {stepStatus && (
          <div className={cn(
            "h-1 w-full transition-all duration-500",
            stepStatus.variant === 'success' && "bg-gradient-to-r from-green-500 to-green-400",
            stepStatus.variant === 'destructive' && "bg-gradient-to-r from-red-500 to-red-400",
            stepStatus.variant === 'default' && "bg-gradient-to-r from-primary to-primary/80 animate-pulse"
          )} />
        )}
        
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-2xl flex items-center space-x-3">
              <div className={cn(
                "w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-300",
                isCompleted && "bg-gradient-to-br from-green-500 to-green-600 shadow-green-500/25",
                isRunning && "bg-gradient-to-br from-primary to-primary/80 shadow-primary/25",
                !isCompleted && !isRunning && "bg-gradient-to-br from-muted to-muted/80"
              )}>
                <span className={cn(
                  "font-bold text-sm transition-colors",
                  (isCompleted || isRunning) && "text-white",
                  !isCompleted && !isRunning && "text-muted-foreground"
                )}>{step.id}</span>
              </div>
              <span>{step.title}</span>
            </CardTitle>
            
            <div className="flex items-center space-x-2">
              {stepStatus && (
                <Badge 
                  variant={stepStatus.variant === 'success' ? 'secondary' : 'outline'}
                  className={cn(
                    "flex items-center space-x-1 transition-all duration-300",
                    stepStatus.variant === 'success' && "status-success",
                    stepStatus.variant === 'destructive' && "status-error",
                    stepStatus.variant === 'default' && "bg-primary/10 text-primary border-primary/20"
                  )}
                >
                  <stepStatus.icon className="w-3 h-3" />
                  <span>{stepStatus.label}</span>
                </Badge>
              )}
              
              {getExecutionTime() && (
                <Badge variant="outline" className="text-xs">
                  {getExecutionTime()}
                </Badge>
              )}
            </div>
          </div>
          
          <CardDescription className="text-base leading-relaxed">
            {step.desc}
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-8">
          <div className="animate-fade-in">
            <StepForm
              step={step}
              selectedLanguage={selectedLanguage}
              formData={formData}
              onFormChange={onFormChange}
            />
          </div>

          {step.action && (
            <div className="flex justify-center">
              <Button
                onClick={onExecute}
                disabled={!canExecute || isRunning}
                size="lg"
                className={cn(
                  "min-w-40 h-12 text-base font-semibold transition-all duration-300 transform-gpu",
                  "bg-gradient-to-r from-primary to-primary/90 hover:from-primary/90 hover:to-primary",
                  "shadow-lg hover:shadow-xl hover:scale-105",
                  "disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                )}
              >
                {isRunning ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-3 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5 mr-3" />
                    Execute Step
                  </>
                )}
              </Button>
            </div>
          )}

          <StepLogs
            logs={execution?.logs || []}
            error={execution?.error}
            isRunning={isRunning}
          />
        </CardContent>
      </Card>

      {/* Enhanced Navigation Footer */}
      <Card className="shadow-lg border-0 bg-gradient-to-r from-card to-card/80 backdrop-blur-sm">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              onClick={onBack}
              disabled={!canGoBack}
              size="lg"
              className={cn(
                "min-w-32 transition-all duration-200",
                canGoBack && "hover:bg-muted/80 hover:scale-105"
              )}
            >
              ← Back
            </Button>
            
            <div className="flex flex-col items-center space-y-2">
              <div className="text-sm font-medium text-muted-foreground">
                Step {step.id} of {visibleSteps.length}
              </div>
              <div className="flex space-x-1">
                {visibleSteps.map((s) => (
                  <div
                    key={s.id}
                    className={cn(
                      "w-2 h-2 rounded-full transition-all duration-300",
                      s.id === step.id && "bg-primary scale-125",
                      completedSteps.includes(s.id) && s.id !== step.id && "bg-green-500",
                      !completedSteps.includes(s.id) && s.id !== step.id && "bg-muted-foreground/30"
                    )}
                  />
                ))}
              </div>
            </div>
            
            <Button
              onClick={onNext}
              disabled={!canGoNext || isRunning}
              size="lg"
              className={cn(
                "min-w-32 transition-all duration-200",
                "bg-gradient-to-r from-primary to-primary/90 hover:from-primary/90 hover:to-primary",
                "shadow-lg hover:shadow-xl",
                (canGoNext && !isRunning) && "hover:scale-105"
              )}
            >
              {isLastStep ? 'Complete' : 'Next'} →
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
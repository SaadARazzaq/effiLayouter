import { useEffect } from 'react';
import { FileText, Zap, Globe, Settings } from 'lucide-react';
import { useWizardStore } from '@/store/wizard';
import { WIZARD_STEPS } from '@/data/steps';
import { WizardStepper } from '@/components/wizard/WizardStepper';
import { WizardStepComponent } from '@/components/wizard/WizardStep';
import { Toaster } from '@/components/ui/toaster';
import { Badge } from '@/components/ui/badge';
import { ThemeToggle } from '@/components/ThemeToggle';

export function WizardPage() {
  const {
    currentStep,
    selectedLanguage,
    executions,
    formData,
    setCurrentStep,
    setSelectedLanguage,
    updateFormData,
    executeStep,
    canProceedToStep
  } = useWizardStore();

  // Handle language selection changes
  useEffect(() => {
    if (formData[2]?.lang && formData[2].lang !== selectedLanguage) {
      setSelectedLanguage(formData[2].lang);
    }
  }, [formData, selectedLanguage, setSelectedLanguage]);

  const currentStepData = WIZARD_STEPS.find(step => step.id === currentStep);
  const completedSteps = Object.keys(executions)
    .map(Number)
    .filter(stepId => executions[stepId]?.status === 'success');
    
  const runningSteps = Object.keys(executions)
    .map(Number)
    .filter(stepId => executions[stepId]?.status === 'running');

  const visibleSteps = WIZARD_STEPS.filter(step => 
    !step.visibleWhen || step.visibleWhen === selectedLanguage
  );

  const isLastVisibleStep = currentStep === Math.max(...visibleSteps.map(s => s.id));

  const handleStepClick = (stepId: number) => {
    if (canProceedToStep(stepId)) {
      setCurrentStep(stepId);
    }
  };

  const handleFormChange = (data: Record<string, any>) => {
    updateFormData(currentStep, data);
  };

  const handleExecute = async () => {
    await executeStep(currentStep);
  };

  const handleNext = () => {
    const nextVisibleStep = visibleSteps.find(step => step.id > currentStep);
    if (nextVisibleStep) {
      setCurrentStep(nextVisibleStep.id);
    }
  };

  const handleBack = () => {
    const prevVisibleStep = visibleSteps
      .filter(step => step.id < currentStep)
      .pop();
    if (prevVisibleStep) {
      setCurrentStep(prevVisibleStep.id);
    }
  };

  const canGoNext = () => {
    if (isLastVisibleStep) return true;
    
    // For steps with actions, require completion
    if (currentStepData?.action) {
      return executions[currentStep]?.status === 'success';
    }
    
    // For steps without actions (like language selection), allow immediate progression
    return true;
  };

  const canExecuteStep = () => {
    if (!currentStepData?.action) return false;
    
    // Check if required form fields are filled
    const stepFormData = formData[currentStep] || {};
    const inputs = currentStepData.conditional 
      ? currentStepData.conditional[selectedLanguage]?.inputs || []
      : currentStepData.inputs || [];

    return inputs.every(input => {
      if (input.type === 'file') {
        return stepFormData[input.id] instanceof File;
      }
      return stepFormData[input.id] !== undefined && stepFormData[input.id] !== '';
    });
  };

  if (!currentStepData) {
    return <div>Step not found</div>;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Background Pattern */}
      <div className="fixed inset-0 bg-gradient-to-br from-primary/5 via-background to-secondary/10 pointer-events-none" />
      <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(120,119,198,0.1),transparent)] pointer-events-none" />
      
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="relative text-center mb-12 animate-fade-in">
          <div className="absolute top-4 right-4">
            <ThemeToggle />
          </div>
          
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary to-primary/80 rounded-2xl mb-6 shadow-lg">
            <FileText className="w-8 h-8 text-primary-foreground" />
          </div>
          
          <h1 className="text-4xl font-bold mb-3 gradient-text">
            EffiLayouter
          </h1>
          <p className="text-xl text-muted-foreground mb-6 max-w-2xl mx-auto leading-relaxed">
            Professional PDF translation with intelligent text extraction and layout preservation
          </p>
          
          <div className="flex items-center justify-center space-x-6 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-muted-foreground">AI-Powered</span>
            </div>
            <div className="flex items-center space-x-2">
              <Zap className="w-4 h-4 text-primary" />
              <span className="text-muted-foreground">Fast Processing</span>
            </div>
            <div className="flex items-center space-x-2">
              <Globe className="w-4 h-4 text-primary" />
              <span className="text-muted-foreground">Multi-Language</span>
            </div>
          </div>
          
          {/* Progress Overview */}
          <div className="mt-8 p-4 bg-card/50 backdrop-blur-sm border rounded-xl">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center space-x-2">
                <Settings className="w-4 h-4 text-muted-foreground" />
                <span className="text-muted-foreground">Pipeline:</span>
                <Badge variant="secondary" className="capitalize">
                  {selectedLanguage}
                </Badge>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-muted-foreground">Progress:</span>
                <Badge variant="outline">
                  {completedSteps.length} / {visibleSteps.length} steps
                </Badge>
              </div>
            </div>
            
            {completedSteps.length > 0 && (
              <div className="mt-3 w-full bg-muted rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-primary to-primary/80 h-2 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${(completedSteps.length / visibleSteps.length) * 100}%` }}
                />
              </div>
            )}
          </div>
        </div>

        <WizardStepper
          steps={WIZARD_STEPS}
          currentStep={currentStep}
          completedSteps={completedSteps}
          runningSteps={runningSteps}
          selectedLanguage={selectedLanguage}
          onStepClick={handleStepClick}
          canProceedToStep={canProceedToStep}
        />

        {/* Current Step */}
        <div className="mt-8 animate-slide-up">
          <WizardStepComponent
            step={currentStepData}
            selectedLanguage={selectedLanguage}
            execution={executions[currentStep]}
            formData={formData[currentStep] || {}}
            onFormChange={handleFormChange}
            onExecute={handleExecute}
            onNext={handleNext}
            onBack={handleBack}
            canGoBack={currentStep > 1}
            canGoNext={canGoNext()}
            canExecute={canExecuteStep()}
            isLastStep={isLastVisibleStep}
            visibleSteps={visibleSteps}
            completedSteps={completedSteps}
          />
        </div>
      </div>
      
      <Toaster />
    </div>
  );
}
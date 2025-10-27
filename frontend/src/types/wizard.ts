export interface WizardStep {
  id: number;
  title: string;
  desc: string;
  inputs?: WizardInput[];
  conditional?: {
    english?: StepConfig;
    arabic?: StepConfig;
  };
  action?: string;
  result?: string;
  visibleWhen?: string;
  viewer?: ViewerConfig;
  actions?: ActionConfig[];
}

export interface WizardInput {
  type: 'file' | 'text' | 'radio' | 'number';
  id: string;
  accept?: string;
  value?: string | number;
  options?: string[];
  min?: number;
  max?: number;
}

export interface StepConfig {
  inputs: WizardInput[];
  action: string;
  result: string;
}

export interface ViewerConfig {
  left: string;
  rightConditional: {
    english: string;
    arabic: string;
  };
}

export interface ActionConfig {
  label: string;
  toConditional?: {
    english: string;
    arabic: string;
  };
}

export interface StepExecution {
  stepId: number;
  status: 'idle' | 'running' | 'success' | 'error';
  logs: string[];
  result?: any;
  error?: string;
}

export interface WizardState {
  currentStep: number;
  selectedLanguage: 'english' | 'arabic';
  executions: Record<number, StepExecution>;
  formData: Record<string, any>;
  setCurrentStep: (step: number) => void;
  setSelectedLanguage: (lang: 'english' | 'arabic') => void;
  updateFormData: (stepId: number, data: Record<string, any>) => void;
  executeStep: (stepId: number) => Promise<void>;
  resetExecution: (stepId: number) => void;
  canProceedToStep: (stepId: number) => boolean;
}
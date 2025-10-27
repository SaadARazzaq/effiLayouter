import { create } from 'zustand';
import { WizardState, StepExecution } from '@/types/wizard';
import { apiClient } from '@/lib/api';
import { toast } from '@/hooks/use-toast';

export const useWizardStore = create<WizardState>((set, get) => ({
  currentStep: 1,
  selectedLanguage: 'english',
  executions: {},
  formData: {
    1: { save_as: 'input.pdf' },
    2: { lang: 'english' },
    3: { input_pdf: 'input.pdf', output_pdf: 'input_text_removed.pdf' },
    4: { json_output: 'extracted_data.json', line_db_output: 'line_db.json' },
    5: { ar_line_db_output: 'ar_line_db.json', max_workers: 2, timeout_seconds: 120 },
    6: {
      json_input: 'extracted_data.json',
      text_removed_pdf: 'input_text_removed.pdf',
      output_pdf: 'english_reconstructed_input.pdf',
      ar_line_db_input: 'ar_line_db.json',
      base_pdf: 'input_text_removed.pdf',
      arabic_output_pdf: 'arabic_reconstructed_input.pdf'
    },
    7: { visualized_pdf: 'input_visualized.pdf' },
    8: {}
  },

  setCurrentStep: (step: number) => set({ currentStep: step }),

  setSelectedLanguage: (lang: 'english' | 'arabic') => {
    set({ selectedLanguage: lang });
    const { updateFormData } = get();
    updateFormData(2, { lang });
  },

  updateFormData: (stepId: number, data: Record<string, any>) =>
    set((state) => ({
      formData: {
        ...state.formData,
        [stepId]: { ...state.formData[stepId], ...data }
      }
    })),

  resetExecution: (stepId: number) =>
    set((state) => ({
      executions: {
        ...state.executions,
        [stepId]: {
          stepId,
          status: 'idle',
          logs: [],
          result: undefined,
          error: undefined
        }
      }
    })),

  executeStep: async (stepId: number) => {
    const state = get();
    const stepData = state.formData[stepId] || {};

    // Update execution status to running
    set((state) => ({
      executions: {
        ...state.executions,
        [stepId]: {
          stepId,
          status: 'running',
          logs: ['Starting step execution...'],
          result: undefined,
          error: undefined
        }
      }
    }));

    try {
      let result;
      const addLog = (message: string) => {
        set((state) => ({
          executions: {
            ...state.executions,
            [stepId]: {
              ...state.executions[stepId],
              logs: [...(state.executions[stepId]?.logs || []), message]
            }
          }
        }));
      };

      switch (stepId) {
        case 1: // Upload PDF
          addLog('Uploading PDF file...');
          result = await apiClient.upload(stepData.file, stepData.save_as);
          break;

        case 2: // Choose Language
          addLog(`Language selected: ${stepData.lang}`);
          result = { ok: true, message: `Selected ${stepData.lang} pipeline` };
          break;

        case 3: // Remove Text
          addLog('Removing text from PDF...');
          result = await apiClient.removeText(stepData.input_pdf, stepData.output_pdf);
          break;

        case 4: // Extract Data
          if (state.selectedLanguage === 'english') {
            addLog('Extracting character data for English...');
            result = await apiClient.extractCharacters(stepData.input_pdf, stepData.json_output);
          } else {
            addLog('Extracting line data for Arabic...');
            result = await apiClient.extractLines('input.pdf', 'line_db.json');
          }
          break;

        case 5: // Translate Arabic
          if (state.selectedLanguage === 'arabic') {
            addLog(`Starting Arabic translation with ${stepData.max_workers} workers...`);
            addLog('Using line_db.json from Step 4...');
            result = await apiClient.translateArabic(
              'line_db.json',
              stepData.ar_line_db_output,
              stepData.max_workers,
              stepData.timeout_seconds
            );
          } else {
            throw new Error('Step 5 is only for Arabic language pipeline');
          }
          break;

        case 6: // Reconstruct PDF
          if (state.selectedLanguage === 'english') {
            addLog('Reconstructing English PDF...');
            result = await apiClient.reconstructEnglish(
              stepData.json_input,
              stepData.text_removed_pdf,
              stepData.output_pdf
            );
          } else {
            addLog('Reconstructing Arabic PDF...');
            result = await apiClient.reconstructArabic(
              stepData.ar_line_db_input,
              stepData.base_pdf,
              stepData.arabic_output_pdf
            );
          }
          break;

        case 7: // Create Visualization
          addLog('Creating line visualization...');
          const lineDbFile = state.selectedLanguage === 'english' ? 'extracted_data.json' : 'line_db.json';
          result = await apiClient.visualizeLines(stepData.input_pdf || 'input.pdf', lineDbFile, stepData.visualized_pdf);
          break;

        case 8: // Comparison
          addLog('Preparing side-by-side comparison...');
          result = { ok: true, message: 'Comparison ready' };
          break;

        default:
          throw new Error(`Unknown step: ${stepId}`);
      }

      if (!result.ok) {
        throw new Error(result.message);
      }

      addLog(result.message);
      
      // Update execution status to success
      set((state) => ({
        executions: {
          ...state.executions,
          [stepId]: {
            ...state.executions[stepId],
            status: 'success',
            result
          }
        }
      }));

      toast({
        title: 'Step Completed',
        description: result.message,
        duration: 3000,
      });

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      
      set((state) => ({
        executions: {
          ...state.executions,
          [stepId]: {
            ...state.executions[stepId],
            status: 'error',
            error: errorMessage,
            logs: [...(state.executions[stepId]?.logs || []), `Error: ${errorMessage}`]
          }
        }
      }));

      toast({
        title: 'Step Failed',
        description: errorMessage,
        variant: 'destructive',
        duration: 5000,
      });
    }
  },

  canProceedToStep: (stepId: number) => {
    const state = get();
    
    switch (stepId) {
      case 1:
        return true;
      case 2:
        return state.executions[1]?.status === 'success';
      case 3:
        return state.executions[2]?.status === 'success';
      case 4:
        return state.executions[3]?.status === 'success';
      case 5:
        return state.selectedLanguage === 'arabic' && state.executions[4]?.status === 'success';
      case 6:
        if (state.selectedLanguage === 'english') {
          return state.executions[4]?.status === 'success';
        } else {
          return state.executions[5]?.status === 'success';
        }
      case 7:
        return state.executions[6]?.status === 'success';
            stepData.output_pdf || 'arabic_reconstructed_input.pdf'
        return state.executions[6]?.status === 'success';
      default:
        return false;
    }
  },
}));
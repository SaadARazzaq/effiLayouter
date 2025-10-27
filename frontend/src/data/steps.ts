import { WizardStep } from '@/types/wizard';

export const WIZARD_STEPS: WizardStep[] = [
  {
    id: 1,
    title: 'Upload PDF',
    desc: 'Choose a PDF file to process.',
    inputs: [
      { type: 'file', accept: '.pdf', id: 'file' },
      { type: 'text', id: 'save_as', value: 'input.pdf' }
    ],
    action: 'upload',
    result: 'input.pdf'
  },
  {
    id: 2,
    title: 'Choose Language',
    desc: 'Select English or Arabic processing pipeline.',
    inputs: [
      { 
        type: 'radio', 
        id: 'lang', 
        options: ['english', 'arabic'], 
        value: 'english' 
      }
    ]
  },
  {
    id: 3,
    title: 'Remove Text',
    desc: 'Create a text-removed base version of the PDF.',
    inputs: [
      { type: 'text', id: 'input_pdf', value: 'input.pdf' },
      { type: 'text', id: 'output_pdf', value: 'input_text_removed.pdf' }
    ],
    action: 'removeText',
    result: 'input_text_removed.pdf'
  },
  {
    id: 4,
    title: 'Extract Data',
    desc: 'Extract character data (English) or line data (Arabic).',
    conditional: {
      english: {
        inputs: [{ type: 'text', id: 'json_output', value: 'extracted_data.json' }],
        action: 'extractCharacters',
        result: 'extracted_data.json'
      },
      arabic: {
        inputs: [{ type: 'text', id: 'line_db_output', value: 'line_db.json' }],
        action: 'extractLines',
        result: 'line_db.json'
      }
    }
  },
  {
    id: 5,
    title: 'Translate (Arabic only)',
    desc: 'Translate Arabic text to target language.',
    visibleWhen: 'arabic',
    inputs: [
      { type: 'text', id: 'ar_line_db_output', value: 'ar_line_db.json' },
      { type: 'number', id: 'max_workers', value: 2, min: 1, max: 8 },
      { type: 'number', id: 'timeout_seconds', value: 120, min: 30, max: 600 }
    ],
    action: 'translateArabic',
    result: 'ar_line_db.json'
  },
  {
    id: 6,
    title: 'Reconstruct PDF',
    desc: 'Overlay translated text back onto the base PDF.',
    conditional: {
      english: {
        inputs: [
          { type: 'text', id: 'json_input', value: 'extracted_data.json' },
          { type: 'text', id: 'text_removed_pdf', value: 'input_text_removed.pdf' },
          { type: 'text', id: 'output_pdf', value: 'english_reconstructed_input.pdf' }
        ],
        action: 'reconstructEnglish',
        result: 'english_reconstructed_input.pdf'
      },
      arabic: {
        inputs: [
          { type: 'text', id: 'ar_line_db_input', value: 'ar_line_db.json' },
          { type: 'text', id: 'base_pdf', value: 'input_text_removed.pdf' },
          { type: 'text', id: 'output_pdf', value: 'arabic_reconstructed_input.pdf' }
        ],
        action: 'reconstructArabic',
        result: 'arabic_reconstructed_input.pdf'
      }
    }
  },
  {
    id: 7,
    title: 'Create Visualization',
    desc: 'Generate line boxes overlay for debugging (optional).',
    inputs: [
      { type: 'text', id: 'visualized_pdf', value: 'input_visualized.pdf' }
    ],
    action: 'visualizeLines',
    result: 'input_visualized.pdf'
  },
  {
    id: 8,
    title: 'Side-by-Side Comparison',
    desc: 'Compare original PDF with final translated version.',
    viewer: {
      left: 'input.pdf',
      rightConditional: {
        english: 'english_reconstructed_input.pdf',
        arabic: 'arabic_reconstructed_input.pdf'
      }
    },
    actions: [
      {
        label: 'Open Final',
        toConditional: {
          english: '/viewer/english_reconstructed_input.pdf',
          arabic: '/viewer/arabic_reconstructed_input.pdf'
        }
      }
    ]
  }
];
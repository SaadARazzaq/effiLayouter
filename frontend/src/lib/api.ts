const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export interface ApiResponse<T = any> {
  ok: boolean;
  message: string;
  output?: {
    filename: string;
    path: string;
    absPath: string;
    size: number;
    modifiedAt: string | null;
  };
  file?: {
    filename: string;
    path: string;
    absPath: string;
    size: number;
    modifiedAt: string | null;
  };
  input?: {
    filename: string;
    path: string;
    absPath: string;
    size: number;
    modifiedAt: string | null;
  };
  preview?: {
    pages: number;
    page_1?: {
      w: number | null;
      h: number | null;
      char_count: number;
    };
  };
  summary?: {
    pages?: number;
    sentences?: number;
    words?: number;
    target_language?: string;
  };
  files?: Array<{
    filename: string;
    path: string;
    absPath: string;
    size: number;
    modifiedAt: string | null;
  }>;
  data?: T;
  detail?: string;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async handleResponse(response: Response): Promise<ApiResponse> {
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.message || data.detail || 'API request failed');
    }
    
    return data;
  }

  async healthCheck(): Promise<ApiResponse> {
    const response = await fetch(`${this.baseUrl}/api/health`);
    return this.handleResponse(response);
  }

  async upload(file: File, saveAs: string = 'input.pdf'): Promise<ApiResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('save_as', saveAs);

    const response = await fetch(`${this.baseUrl}/api/upload`, {
      method: 'POST',
      body: formData,
    });

    return this.handleResponse(response);
  }

  async removeText(inputPdf: string = 'input.pdf', outputPdf: string = 'input_text_removed.pdf'): Promise<ApiResponse> {
    const formData = new FormData();
    formData.append('input_pdf', inputPdf);
    formData.append('output_pdf', outputPdf);

    const response = await fetch(`${this.baseUrl}/api/remove-text`, {
      method: 'POST',
      body: formData,
    });

    return this.handleResponse(response);
  }

  async extractCharacters(inputPdf: string = 'input.pdf', jsonOutput: string = 'extracted_data.json'): Promise<ApiResponse> {
    const response = await fetch(`${this.baseUrl}/api/extract-characters`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        input_pdf: inputPdf, 
        json_output: jsonOutput 
      }),
    });

    return this.handleResponse(response);
  }

  async extractLines(inputPdf: string = 'input.pdf', lineDbOutput: string = 'line_db.json'): Promise<ApiResponse> {
    const response = await fetch(`${this.baseUrl}/api/extract-lines`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        input_pdf: inputPdf, 
        line_db_output: lineDbOutput 
      }),
    });

    return this.handleResponse(response);
  }

  async translateArabic(
    lineDbInput: string = 'line_db.json',
    arLineDbOutput: string = 'ar_line_db.json',
    maxWorkers: number = 2,
    timeoutSeconds: number = 120
  ): Promise<ApiResponse> {
    const response = await fetch(`${this.baseUrl}/api/translate/arabic`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        line_db_input: lineDbInput,
        ar_line_db_output: arLineDbOutput,
        max_workers: maxWorkers,
        timeout_seconds: timeoutSeconds,
      }),
    });

    return this.handleResponse(response);
  }

  async reconstructEnglish(
    jsonInput: string = 'extracted_data.json',
    textRemovedPdf: string = 'input_text_removed.pdf',
    outputPdf: string = 'english_reconstructed_input.pdf'
  ): Promise<ApiResponse> {
    const response = await fetch(`${this.baseUrl}/api/reconstruct/english`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        json_input: jsonInput,
        text_removed_pdf: textRemovedPdf,
        output_pdf: outputPdf,
      }),
    });

    return this.handleResponse(response);
  }

  async reconstructArabic(
    arLineDbInput: string = 'ar_line_db.json',
    basePdf: string = 'input_text_removed.pdf',
    outputPdf: string = 'arabic_reconstructed_input.pdf'
  ): Promise<ApiResponse> {
    const response = await fetch(`${this.baseUrl}/api/reconstruct/arabic`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ar_line_db_input: arLineDbInput,
        base_pdf: basePdf,
        output_pdf: outputPdf,
      }),
    });

    return this.handleResponse(response);
  }

  async visualizeLines(
    inputPdf: string = 'input.pdf', 
    lineDbInput: string = 'line_db.json', 
    visualizedPdf: string = 'input_visualized.pdf'
  ): Promise<ApiResponse> {
    const response = await fetch(`${this.baseUrl}/api/visualize-lines`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input_pdf: inputPdf,
        line_db_input: lineDbInput,
        visualized_pdf: visualizedPdf,
      }),
    });

    return this.handleResponse(response);
  }

  async listFiles(): Promise<ApiResponse> {
    const response = await fetch(`${this.baseUrl}/api/list`);
    return this.handleResponse(response);
  }

  getFileUrl(filename: string): string {
    return `${this.baseUrl}/api/download?file=${filename}`;
  }
}

export const apiClient = new ApiClient();
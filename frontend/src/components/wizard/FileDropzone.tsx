import { useCallback, useState } from 'react';
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

interface FileDropzoneProps {
  accept?: string;
  maxSize?: number; // in MB
  onFileSelect: (file: File) => void;
  value?: File;
  className?: string;
}

export function FileDropzone({ 
  accept = '.pdf', 
  maxSize = 100, 
  onFileSelect, 
  value,
  className 
}: FileDropzoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState<string>('');

  const validateFile = useCallback((file: File) => {
    setError('');
    
    if (accept && !file.name.toLowerCase().endsWith(accept.replace('.', ''))) {
      setError(`Please select a ${accept} file`);
      return false;
    }

    if (file.size > maxSize * 1024 * 1024) {
      setError(`File size must be less than ${maxSize}MB`);
      return false;
    }

    return true;
  }, [accept, maxSize]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      const file = files[0];
      if (validateFile(file)) {
        onFileSelect(file);
      }
    }
  }, [onFileSelect, validateFile]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      const file = files[0];
      if (validateFile(file)) {
        onFileSelect(file);
      }
    }
  }, [onFileSelect, validateFile]);

  const clearFile = () => {
    setError('');
    // Create a new file input to clear the selection
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = accept;
    input.onchange = (e) => {
      const target = e.target as HTMLInputElement;
      if (target.files && target.files.length > 0) {
        const file = target.files[0];
        if (validateFile(file)) {
          onFileSelect(file);
        }
      }
    };
    input.click();
  };

  return (
    <div className={cn("w-full", className)}>
      {!value ? (
        <div
          onDrop={handleDrop}
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          className={cn(
            "relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200",
            "hover:border-primary/50 hover:bg-primary/5 hover:shadow-lg",
            isDragOver && "border-primary bg-primary/10 shadow-lg scale-[1.02]",
            error && "border-destructive bg-destructive/5 shadow-lg shadow-destructive/10"
          )}
        >
          {/* Animated background effect */}
          <div className={cn(
            "absolute inset-0 rounded-lg opacity-0 transition-opacity duration-300",
            isDragOver && "opacity-100 bg-gradient-to-br from-primary/5 to-primary/10"
          )} />
          
          <Upload className={cn(
            "w-12 h-12 mx-auto mb-4 transition-all duration-300",
            isDragOver && "text-primary",
            error && "text-destructive",
            !isDragOver && !error && "text-muted-foreground hover:text-primary"
          )} />
          
          <div className="space-y-3 relative z-10">
            <p className="text-lg font-semibold">
              Drop your PDF here, or{" "}
              <label className="text-primary hover:text-primary/80 cursor-pointer underline decoration-2 underline-offset-2 transition-all duration-200 hover:decoration-primary/60">
                browse files
                <input
                  type="file"
                  accept={accept}
                  onChange={handleFileInput}
                  className="hidden"
                  aria-label="Choose PDF file"
                />
              </label>
            </p>
            <div className="flex items-center justify-center space-x-4 text-sm text-muted-foreground">
              <Badge variant="outline" className="bg-muted/50">
                Max {maxSize}MB
              </Badge>
              <Badge variant="outline" className="bg-muted/50">
                PDF Only
              </Badge>
            </div>
          </div>
        </div>
      ) : (
        <div className="border rounded-lg p-4 bg-gradient-to-r from-green-50 to-green-50/50 border-green-200 dark:from-green-950/50 dark:to-green-950/20 dark:border-green-800 animate-scale-in">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <File className="w-8 h-8 text-green-600 dark:text-green-400" />
                <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400 absolute -top-1 -right-1 bg-background rounded-full" />
              </div>
              <div>
                <p className="font-semibold text-green-800 dark:text-green-200">{value.name}</p>
                <div className="flex items-center space-x-2">
                  <p className="text-sm text-green-600 dark:text-green-400">
                    {(value.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                  <Badge variant="secondary" className="text-xs bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300">
                    Ready
                  </Badge>
                </div>
              </div>
            </div>
            <button
              onClick={clearFile}
              className="p-2 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-md transition-all duration-200 hover:scale-110 group"
              aria-label="Remove file"
            >
              <X className="w-4 h-4 text-muted-foreground group-hover:text-red-500 transition-colors" />
            </button>
          </div>
        </div>
      )}
      
      {error && (
        <div className="mt-3 p-3 bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 rounded-lg animate-scale-in">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-500" />
            <span className="text-sm font-medium text-red-700 dark:text-red-300">
              {error}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
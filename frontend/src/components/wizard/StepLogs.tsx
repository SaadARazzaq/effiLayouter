import { useState } from 'react';
import { ChevronDown, ChevronRight, AlertCircle, Terminal, CheckCircle, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';

interface StepLogsProps {
  logs: string[];
  error?: string;
  isRunning?: boolean;
}

export function StepLogs({ logs = [], error, isRunning }: StepLogsProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (logs.length === 0 && !error) {
    return null;
  }

  return (
    <div className="mt-6 border rounded-lg overflow-hidden shadow-sm bg-gradient-to-br from-muted/20 to-muted/10 backdrop-blur-sm">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-muted/40 to-muted/20 hover:from-muted/60 hover:to-muted/40 transition-all duration-200 group"
      >
        <div className="flex items-center space-x-3">
          <Terminal className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-all duration-200" />
          ) : (
            <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-all duration-200" />
          )}
          <span className="font-semibold text-sm">
            Execution Logs
          </span>
          
          {error && (
            <Badge variant="destructive" className="text-xs">
              Error
            </Badge>
          )}
          
          {isRunning && (
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
              <Badge variant="outline" className="text-xs bg-primary/10 text-primary border-primary/20">
                Running
              </Badge>
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="text-xs">
            {logs.length} {logs.length === 1 ? 'entry' : 'entries'}
          </Badge>
          {logs.length > 0 && !error && (
            <CheckCircle className="w-4 h-4 text-green-500" />
          )}
        </div>
      </button>

      {isExpanded && (
        <div className="border-t animate-slide-up">
          {error && (
            <Alert variant="destructive" className="m-4 mb-0 shadow-sm">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="font-medium">{error}</AlertDescription>
            </Alert>
          )}
          
          {logs.length > 0 && (
            <div className="p-4 bg-gradient-to-br from-muted/5 to-muted/10 space-y-2 max-h-48 overflow-y-auto logs-container">
              {logs.map((log, index) => {
                const isError = log.startsWith('Error:');
                const isSuccess = log.includes('successfully') || log.includes('completed') || log.includes('ready');
                
                return (
                  <div
                    key={index}
                    className={cn(
                      "text-xs font-mono p-3 rounded-lg border-l-4 transition-all duration-200 hover:shadow-sm",
                      isError && "bg-red-50 border-red-400 text-red-800 dark:bg-red-950/50 dark:border-red-600 dark:text-red-200",
                      isSuccess && "bg-green-50 border-green-400 text-green-800 dark:bg-green-950/50 dark:border-green-600 dark:text-green-200",
                      !isError && !isSuccess && "bg-blue-50 border-blue-400 text-blue-800 dark:bg-blue-950/50 dark:border-blue-600 dark:text-blue-200"
                    )}
                  >
                    <div className="flex items-start space-x-2">
                      <span className="text-muted-foreground font-medium min-w-8">
                        {String(index + 1).padStart(2, '0')}
                      </span>
                      <span className="flex-1">{log}</span>
                      {isSuccess && <CheckCircle className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />}
                      {isError && <AlertCircle className="w-3 h-3 text-red-500 mt-0.5 flex-shrink-0" />}
                      {!isError && !isSuccess && <Clock className="w-3 h-3 text-blue-500 mt-0.5 flex-shrink-0" />}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
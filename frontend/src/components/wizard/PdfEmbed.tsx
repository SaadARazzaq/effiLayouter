import { useState } from 'react';
import { FileText, Download, ExternalLink, Maximize2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { apiClient } from '@/lib/api';

interface PdfEmbedProps {
  filename: string;
  title?: string;
  className?: string;
}

export function PdfEmbed({ filename, title, className }: PdfEmbedProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const fileUrl = apiClient.getFileUrl(filename);

  const handleLoad = () => {
    setIsLoading(false);
    setHasError(false);
  };

  const handleError = () => {
    setIsLoading(false);
    setHasError(true);
  };

  const handleDownload = () => {
    window.open(fileUrl, '_blank');
  };

  const handleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const handleViewExternal = () => {
    window.open(`/viewer/${filename}`, '_blank');
  };

  return (
    <div className={cn(
      "flex flex-col h-full transition-all duration-300",
      isFullscreen && "fixed inset-4 z-50 bg-background rounded-lg shadow-2xl",
      className
    )}>
      {title && (
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-muted/30 to-muted/10 backdrop-blur-sm">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-primary/10 rounded-md flex items-center justify-center">
              <FileText className="w-3 h-3 text-primary" />
            </div>
            <span className="font-semibold text-sm">{title}</span>
            <Badge variant="outline" className="text-xs bg-background/50">
              PDF
            </Badge>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDownload}
              className="h-8 px-3 hover:bg-muted/80 transition-all duration-200 hover:scale-105"
              title="Download PDF"
            >
              <Download className="w-3 h-3 mr-1" />
              <span className="text-xs">Download</span>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleFullscreen}
              className="h-8 px-3 hover:bg-muted/80 transition-all duration-200 hover:scale-105"
              title="Toggle fullscreen"
            >
              <Maximize2 className="w-3 h-3 mr-1" />
              <span className="text-xs">Expand</span>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleViewExternal}
              className="h-8 px-3 hover:bg-muted/80 transition-all duration-200 hover:scale-105"
              title="Open in new tab"
            >
              <ExternalLink className="w-3 h-3 mr-1" />
              <span className="text-xs">Open</span>
            </Button>
          </div>
        </div>
      )}
      
      <div className="flex-1 relative bg-gradient-to-br from-muted/5 to-muted/10">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm">
            <div className="text-center space-y-4">
              <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin mx-auto" />
              <div className="space-y-2">
                <p className="text-sm font-medium">Loading PDF...</p>
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          </div>
        )}

        {hasError && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm">
            <div className="text-center space-y-4 p-6">
              <div className="w-16 h-16 bg-red-100 dark:bg-red-950/50 rounded-full flex items-center justify-center mx-auto">
                <FileText className="w-8 h-8 text-red-500" />
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium text-red-700 dark:text-red-300">Unable to load PDF</p>
                <p className="text-xs text-muted-foreground">The file might be corrupted or not accessible</p>
              </div>
              <Button
                variant="default"
                size="sm"
                onClick={handleDownload}
                className="bg-gradient-to-r from-primary to-primary/90 hover:shadow-lg transition-all duration-200"
              >
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
            </div>
          </div>
        )}

        <embed
          src={fileUrl}
          type="application/pdf"
          width="100%"
          height="100%"
          onLoad={handleLoad}
          onError={handleError}
          className={cn(
            "w-full h-full border-0 rounded-lg shadow-inner",
            "min-h-[400px] max-h-full object-contain",
            (isLoading || hasError) && "invisible"
          )}
          title={`PDF Viewer: ${filename}`}
        />
        
        {/* Overlay for fullscreen exit */}
        {isFullscreen && (
          <div className="absolute top-4 right-4 z-10">
            <Button
              variant="secondary"
              size="sm"
              onClick={handleFullscreen}
              className="shadow-lg"
            >
              Exit Fullscreen
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
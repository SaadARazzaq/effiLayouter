import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { PdfEmbed } from '@/components/wizard/PdfEmbed';
import { apiClient } from '@/lib/api';
import { ThemeToggle } from '@/components/ThemeToggle';

export function ViewerPage() {
  const { filename } = useParams<{ filename: string }>();
  const navigate = useNavigate();

  if (!filename) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-muted/20 to-background">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 dark:bg-red-950/50 rounded-full flex items-center justify-center mx-auto mb-4">
            <FileText className="w-8 h-8 text-red-500" />
          </div>
          <h1 className="text-2xl font-bold mb-4">File not found</h1>
          <p className="text-muted-foreground mb-6">The requested PDF file could not be located.</p>
          <Button onClick={() => navigate('/')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Wizard
          </Button>
        </div>
      </div>
    );
  }

  const handleDownload = () => {
    window.open(apiClient.getFileUrl(filename), '_blank');
  };
  
  const getFileType = (filename: string) => {
    if (filename.includes('reconstructed')) return 'Translated';
    if (filename.includes('visualized')) return 'Visualization';
    if (filename.includes('text_removed')) return 'Text Removed';
    return 'Original';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-background flex flex-col">
      {/* Header */}
      <div className="border-b bg-gradient-to-r from-card to-card/80 backdrop-blur-sm shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                onClick={() => navigate('/')}
                className="flex items-center space-x-2 hover:bg-muted/80 transition-all duration-200 hover:scale-105"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Wizard</span>
              </Button>
              
              <div>
                <div className="flex items-center space-x-2">
                  <h1 className="text-xl font-semibold">{filename}</h1>
                  <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">
                    {getFileType(filename)}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">Professional PDF Viewer</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <ThemeToggle />
              <Button 
                onClick={handleDownload} 
                className="flex items-center space-x-2 bg-gradient-to-r from-primary to-primary/90 hover:shadow-lg transition-all duration-200 hover:scale-105"
              >
                <Download className="w-4 h-4" />
                <span>Download</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* PDF Viewer */}
      <div className="flex-1 p-6">
        <div className="h-full max-w-6xl mx-auto animate-fade-in">
          <PdfEmbed 
            filename={filename} 
            className="h-full border-0 rounded-xl shadow-2xl bg-gradient-to-br from-card to-card/80"
          />
        </div>
      </div>
    </div>
  );
}
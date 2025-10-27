import { useState, useEffect } from 'react';
import { GripVertical, ArrowLeftRight } from 'lucide-react';
import { PdfEmbed } from './PdfEmbed';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SplitViewProps {
  leftFile: string;
  rightFile: string;
  leftTitle?: string;
  rightTitle?: string;
  className?: string;
}

export function SplitView({ 
  leftFile, 
  rightFile, 
  leftTitle = 'Original', 
  rightTitle = 'Translated',
  className 
}: SplitViewProps) {
  const [leftWidth, setLeftWidth] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    e.preventDefault();
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return;

    const container = document.getElementById('split-container');
    if (!container) return;

    const rect = container.getBoundingClientRect();
    const newLeftWidth = ((e.clientX - rect.left) / rect.width) * 100;
    
    // Constrain between 20% and 80%
    setLeftWidth(Math.min(80, Math.max(20, newLeftWidth)));
  };

  const handleReset = () => {
    setIsAnimating(true);
    setLeftWidth(50);
    setTimeout(() => setIsAnimating(false), 300);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Add global mouse event listeners
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isDragging]);

  return (
    <div className="relative">
      {/* Control Panel */}
      <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10 flex items-center space-x-2">
        <Button
          variant="secondary"
          size="sm"
          onClick={handleReset}
          className="shadow-lg backdrop-blur-sm bg-background/80 hover:bg-background/90 transition-all duration-200"
          title="Reset to 50/50 split"
        >
          <ArrowLeftRight className="w-3 h-3 mr-1" />
          Reset
        </Button>
      </div>
      
      <div 
        id="split-container"
        className={cn(
          "flex h-full border rounded-lg overflow-hidden shadow-xl bg-gradient-to-br from-card to-card/80 min-h-[500px]",
          className
        )}
      >
        {/* Left Panel */}
        <div 
          style={{ 
            width: `${leftWidth}%`,
            transition: isAnimating ? 'width 0.3s ease-out' : 'none'
          }}
          className="border-r border-border/50 h-full overflow-hidden"
        >
          <PdfEmbed filename={leftFile} title={leftTitle} />
        </div>

        {/* Resizer */}
        <div
          onMouseDown={handleMouseDown}
          className={cn(
            "relative w-2 bg-gradient-to-b from-border/50 to-border cursor-col-resize transition-all duration-200 flex-shrink-0 group",
            "hover:bg-gradient-to-b hover:from-primary/30 hover:to-primary/50 hover:w-3",
            isDragging && "bg-gradient-to-b from-primary to-primary/80 w-3 shadow-lg"
          )}
          role="separator"
          aria-label="Resize panels"
        >
          <div className="absolute inset-0 flex items-center justify-center">
            <GripVertical className={cn(
              "w-3 h-3 text-muted-foreground/50 transition-all duration-200",
              "group-hover:text-primary group-hover:scale-110",
              isDragging && "text-primary scale-125"
            )} />
          </div>
          
          {/* Resize indicator */}
          <div className={cn(
            "absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2",
            "w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center",
            "opacity-0 group-hover:opacity-100 transition-opacity duration-200",
            isDragging && "opacity-100 bg-primary/20"
          )}>
            <ArrowLeftRight className="w-3 h-3 text-primary" />
          </div>
        </div>

        {/* Right Panel */}
        <div 
          style={{ 
            width: `${100 - leftWidth}%`,
            transition: isAnimating ? 'width 0.3s ease-out' : 'none'
          }}
          className="flex-1 h-full overflow-hidden"
        >
          <PdfEmbed filename={rightFile} title={rightTitle} />
        </div>
      </div>
    </div>
  );
}
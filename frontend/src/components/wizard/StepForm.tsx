import { useState } from 'react';
import { Settings, FileText, Globe, Cpu, CheckCircle } from 'lucide-react';
import { WizardStep, WizardInput } from '@/types/wizard';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { FileDropzone } from './FileDropzone';
import { cn } from '@/lib/utils';


interface StepFormProps {
  step: WizardStep;
  selectedLanguage: 'english' | 'arabic';
  formData: Record<string, any>;
  onFormChange: (data: Record<string, any>) => void;
}

export function StepForm({ step, selectedLanguage, formData, onFormChange }: StepFormProps) {
  const [localData, setLocalData] = useState(formData || {});

  // Get the appropriate inputs based on language
  const getInputs = (): WizardInput[] => {
    if (step.conditional) {
      return step.conditional[selectedLanguage]?.inputs || [];
    }
    return step.inputs || [];
  };

  const handleInputChange = (inputId: string, value: any) => {
    const newData = { ...localData, [inputId]: value };
    setLocalData(newData);
    onFormChange(newData);
  };

  const inputs = getInputs();

  const getInputIcon = (type: string) => {
    switch (type) {
      case 'file': return FileText;
      case 'radio': return Globe;
      case 'number': return Cpu;
      default: return Settings;
    }
  };

  if (inputs.length === 0) {
    return (
      <Card className="p-8 text-center bg-gradient-to-br from-muted/20 to-muted/10 border-dashed">
        <Settings className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
        <p className="text-muted-foreground font-medium">
          No configuration needed for this step
        </p>
        <p className="text-sm text-muted-foreground/80 mt-2">
          This step will execute automatically
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {inputs.map((input, index) => {
        const Icon = getInputIcon(input.type);
        const inputLabel = input.id.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        return (
          <Card key={input.id} className="p-6 bg-gradient-to-br from-card to-card/80 border-0 shadow-sm hover:shadow-md transition-all duration-200">
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Icon className="w-4 h-4 text-primary" />
                </div>
                <div className="flex-1">
                  <Label htmlFor={input.id} className="text-base font-semibold flex items-center space-x-2">
                    <span>{inputLabel}</span>
                    {input.type === 'file' && (
                      <Badge variant="outline" className="text-xs">Required</Badge>
                    )}
                  </Label>
                  {input.type === 'number' && (
                    <p className="text-sm text-muted-foreground mt-1">
                      Range: {input.min} - {input.max}
                    </p>
                  )}
                </div>
              </div>
              
              <div className="pl-11">
                {input.type === 'file' && (
                  <FileDropzone
                    accept={input.accept}
                    onFileSelect={(file) => handleInputChange(input.id, file)}
                    value={localData[input.id]}
                  />
                )}
                
                {input.type === 'text' && (
                  <Input
                    id={input.id}
                    type="text"
                    value={localData[input.id] || input.value || ''}
                    onChange={(e) => handleInputChange(input.id, e.target.value)}
                    placeholder={`Enter ${input.id.replace(/_/g, ' ')}`}
                    className="bg-background/50 border-muted-foreground/20 focus:border-primary focus:bg-background transition-all duration-200"
                  />
                )}
                
                {input.type === 'number' && (
                  <div className="space-y-2">
                    <Input
                      id={input.id}
                      type="number"
                      min={input.min}
                      max={input.max}
                      value={localData[input.id] || input.value || ''}
                      onChange={(e) => handleInputChange(input.id, parseInt(e.target.value))}
                      className="bg-background/50 border-muted-foreground/20 focus:border-primary focus:bg-background transition-all duration-200"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>Min: {input.min}</span>
                      <span>Max: {input.max}</span>
                    </div>
                  </div>
                )}
                
                {input.type === 'radio' && input.options && (
                  <RadioGroup
                    value={localData[input.id] || input.value}
                    onValueChange={(value) => handleInputChange(input.id, value)}
                    className="space-y-3"
                  >
                    {input.options.map((option) => (
                      <Card 
                        key={option} 
                        className={cn(
                          "p-4 cursor-pointer transition-all duration-200 hover:shadow-md border-2",
                          (localData[input.id] || input.value) === option 
                            ? "border-primary bg-primary/5 shadow-sm" 
                            : "border-muted hover:border-muted-foreground/40"
                        )}
                        onClick={() => handleInputChange(input.id, option)}
                      >
                        <div className="flex items-center space-x-3">
                          <RadioGroupItem value={option} id={option} />
                          <div className="flex-1">
                            <Label htmlFor={option} className="text-base font-medium capitalize cursor-pointer">
                              {option}
                            </Label>
                            <p className="text-sm text-muted-foreground mt-1">
                              {option === 'english' 
                                ? 'Character-based extraction for Latin scripts' 
                                : 'Line-based extraction with RTL support'
                              }
                            </p>
                          </div>
                          {(localData[input.id] || input.value) === option && (
                            <CheckCircle className="w-5 h-5 text-primary" />
                          )}
                        </div>
                      </Card>
                    ))}
                  </RadioGroup>
                )}
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
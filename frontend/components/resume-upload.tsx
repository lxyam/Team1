import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, File, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface ResumeUploadProps {
  onFileAccepted: (file: File) => void;
  onAnalyzeClick: () => void;
}

export function ResumeUpload({ onFileAccepted, onAnalyzeClick }: ResumeUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setError(null);
    if (acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0];
      const fileExtension = selectedFile.name.split('.').pop()?.toLowerCase();
      
      if (fileExtension === 'pdf' || fileExtension === 'doc' || fileExtension === 'docx') {
        setFile(selectedFile);
        onFileAccepted(selectedFile);
      } else {
        setError('请上传 PDF, DOC 或 DOCX 格式的简历文件');
      }
    }
  }, [onFileAccepted]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1
  });

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-8">
        <h2 className="text-xl font-semibold text-slate-800 mb-6">上传您的简历</h2>
        
        <div 
          {...getRootProps()} 
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
            isDragActive 
              ? "border-primary-400 bg-primary-50" 
              : "border-slate-300 hover:border-primary-400 hover:bg-slate-50",
            error && "border-red-300"
          )}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center space-y-4">
            {file ? (
              <>
                <CheckCircle2 className="h-12 w-12 text-green-500" />
                <div className="flex items-center space-x-2">
                  <File className="h-5 w-5 text-slate-400" />
                  <span className="text-slate-700 font-medium">{file.name}</span>
                </div>
              </>
            ) : (
              <>
                <UploadCloud className="h-12 w-12 text-slate-400" />
                <div className="space-y-1">
                  <p className="text-lg font-medium text-slate-700">
                    {isDragActive ? "释放文件以上传" : "拖拽文件到此处或点击上传"}
                  </p>
                  <p className="text-sm text-slate-500">
                    支持 PDF, DOC, DOCX 格式 (最大 10MB)
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
        
        {error && (
          <div className="mt-3 flex items-center text-red-500 text-sm">
            <AlertCircle className="h-4 w-4 mr-1 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
        
        <div className="mt-8 flex justify-end">
          <Button 
            disabled={!file} 
            onClick={onAnalyzeClick}
            size="lg"
          >
            开始分析
          </Button>
        </div>
      </div>
    </div>
  );
} 
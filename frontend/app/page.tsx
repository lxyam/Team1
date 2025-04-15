"use client";

import React, { useState } from 'react';
import { ResumeUpload } from '@/components/resume-upload';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  const handleFileAccepted = (file: File) => {
    setFile(file);
  };

  const handleAnalyzeClick = () => {
    setIsLoading(true);
    
    // Simulate API call delay
    setTimeout(() => {
      setIsLoading(false);
      router.push('/evaluation');
    }, 1500);
  };

  return (
    <div className="py-8">
      <div className="max-w-3xl mx-auto mb-12 text-center">
        <h1 className="text-3xl font-bold text-slate-900 mb-4">智能简历分析系统</h1>
        <p className="text-xl text-slate-600">
          上传您的技术简历，检测内容是否经得起深度提问，发现潜在问题并提供改进建议
        </p>
      </div>

      <ResumeUpload 
        onFileAccepted={handleFileAccepted}
        onAnalyzeClick={handleAnalyzeClick}
      />
      
      <div className="mt-12 max-w-3xl mx-auto">
        <div className="bg-slate-50 rounded-lg p-6 border border-slate-200">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">如何使用这个工具</h2>
          <ol className="space-y-3 text-slate-700 list-decimal pl-5">
            <li>上传您的简历文件（支持 PDF、DOC、DOCX 格式）</li>
            <li>系统会分析您的简历内容，找出可能需要补充说明的地方</li>
            <li>您可以对这些地方进行补充说明，完善您的简历内容</li>
            <li>系统会根据完整信息生成面试问题，模拟真实面试过程</li>
            <li>您需要回答这些问题，系统可能会根据您的回答进行追问</li>
            <li>最后，系统会对您的表现进行综合评估，并给出改进建议</li>
          </ol>
        </div>
      </div>
    </div>
  );
} 
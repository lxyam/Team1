"use client";

import React, { useState } from 'react';
import { SupplementaryInfo } from '@/components/supplementary-info';
import { useRouter } from 'next/navigation';
import { mockResumeEvaluation } from '@/lib/mock-data';

export default function EvaluationPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (supplements: Record<string, string>) => {
    setIsSubmitting(true);
    
    // In a real application, we would send the supplementary information to the backend
    console.log('Supplementary information:', supplements);
    
    // Simulate API call delay
    setTimeout(() => {
      setIsSubmitting(false);
      router.push('/interview');
    }, 1000);
  };

  return (
    <div className="py-8">
      <div className="max-w-4xl mx-auto mb-12 text-center">
        <h1 className="text-3xl font-bold text-slate-900 mb-4">简历评估结果</h1>
        <p className="text-xl text-slate-600">
          我们分析了您的简历，以下是可能需要补充的信息
        </p>
      </div>

      <SupplementaryInfo 
        resumeEvaluation={mockResumeEvaluation}
        onSubmit={handleSubmit}
      />
    </div>
  );
} 
"use client";

import React from 'react';
import { AssessmentResult } from '@/components/assessment-result';
import { useRouter } from 'next/navigation';
import { mockAssessmentResult } from '@/lib/mock-data';

export default function AssessmentPage() {
  const router = useRouter();

  const handleRestart = () => {
    router.push('/');
  };

  return (
    <div className="py-8">
      <div className="max-w-4xl mx-auto mb-8 text-center">
        <h1 className="text-3xl font-bold text-slate-900 mb-4">评估结果</h1>
        <p className="text-xl text-slate-600">
          基于您的简历内容和问答表现，系统给出以下评估结果
        </p>
      </div>

      <AssessmentResult 
        result={mockAssessmentResult}
        onRestart={handleRestart}
      />
    </div>
  );
} 
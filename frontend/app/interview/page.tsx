"use client";

import React, { useState } from 'react';
import { InterviewQuestions } from '@/components/interview-questions';
import { useRouter } from 'next/navigation';
import { mockInterviewQuestions } from '@/lib/mock-data';

interface AnswerData {
  questionId: string;
  answer: string;
  isFollowUp?: boolean;
}

export default function InterviewPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleComplete = (answers: AnswerData[]) => {
    setIsSubmitting(true);
    
    // In a real application, we would send the answers to the backend for evaluation
    console.log('All answers:', answers);
    
    // Simulate API call delay
    setTimeout(() => {
      setIsSubmitting(false);
      router.push('/assessment');
    }, 1500);
  };

  return (
    <div className="py-8">
      <div className="max-w-4xl mx-auto mb-8 text-center">
        <h1 className="text-3xl font-bold text-slate-900 mb-4">模拟面试</h1>
        <p className="text-xl text-slate-600">
          回答以下问题，系统会根据您的回答进行评估
        </p>
      </div>

      <InterviewQuestions
        questions={mockInterviewQuestions}
        onComplete={handleComplete}
      />
    </div>
  );
} 
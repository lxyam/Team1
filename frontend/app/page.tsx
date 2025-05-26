"use client";

import { useState } from 'react';
import { ResumeUpload } from '@/components/resume-upload';
import { InterviewQuestions } from '@/components/interview-questions';
import { AssessmentResult } from '@/components/assessment-result';
import { uploadResume, evaluateInterview, type ResumeData, type AnswerData } from '@/lib/api';

// 将等级评分转换为数字分数
const gradeToScore = (grade: string): number => {
  switch (grade) {
    case 'A': return 90;
    case 'B': return 75;
    case 'C': return 60;
    case 'D': return 40;
    default: return 60;
  }
};

// 处理评估结果，将后端格式转换为前端需要的格式
const processAssessmentResult = (rawResult: any) => {
  if (!rawResult) return null;

  // 收集所有评估数据
  const allEvaluations: any[] = [];
  
  // 项目评估
  if (rawResult.project_qa && Array.isArray(rawResult.project_qa)) {
    allEvaluations.push(...rawResult.project_qa.map((item: any) => item.evaluation).filter(Boolean));
  }
  
  // 优势评估
  if (rawResult.advantages && rawResult.advantages.evaluation) {
    allEvaluations.push(rawResult.advantages.evaluation);
  }
  
  // 编程评估
  if (rawResult.code && rawResult.code.evaluation) {
    allEvaluations.push(rawResult.code.evaluation);
  }

  if (allEvaluations.length === 0) {
    return {
      overallScore: 60,
      categoriesScore: {
        '技术深度': 60,
        '表达能力': 60,
        '项目理解': 60,
        '问题解决能力': 60
      },
      strengths: ['暂无评估数据'],
      improvements: ['请确保回答完整性'],
      suggestions: '建议提供更详细的回答'
    };
  }

  // 计算各维度平均分
  const categories = ['技术深度', '表达能力', '项目理解', '问题解决能力'];
  const categoriesScore: { [key: string]: number } = {};
  
  categories.forEach(category => {
    const scores = allEvaluations
      .filter(evaluation => evaluation[category] && evaluation[category].评分)
      .map(evaluation => gradeToScore(evaluation[category].评分));
    
    categoriesScore[category] = scores.length > 0 
      ? Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length)
      : 60;
  });

  // 计算总分
  const overallScore = Math.round(
    Object.values(categoriesScore).reduce((sum, score) => sum + score, 0) / categories.length
  );

  // 收集优势和改进建议
  const strengths: string[] = [];
  const improvements: string[] = [];
  
  allEvaluations.forEach(evaluation => {
    categories.forEach(category => {
      if (evaluation[category] && evaluation[category].理由) {
        const grade = evaluation[category].评分;
        const reason = evaluation[category].理由;
        
        if (grade === 'A' || grade === 'B') {
          strengths.push(`${category}: ${reason}`);
        } else if (grade === 'C' || grade === 'D') {
          improvements.push(`${category}: ${reason}`);
        }
      }
    });
  });

  // 构建详细评估数据
  const detailedEvaluations: any[] = [];
  
  // 项目评估
  if (rawResult.project_qa && Array.isArray(rawResult.project_qa)) {
    rawResult.project_qa.forEach((item: any) => {
      if (item.evaluation) {
        detailedEvaluations.push({
          question: item.question,
          userAnswer: item.user_answer,
          referenceAnswer: item.reference_answer,
          evaluation: item.evaluation,
          category: '项目经历'
        });
      }
    });
  }
  
  // 优势评估
  if (rawResult.advantages && rawResult.advantages.evaluation) {
    detailedEvaluations.push({
      question: rawResult.advantages.question,
      userAnswer: rawResult.advantages.user_answer,
      referenceAnswer: rawResult.advantages.reference_answer,
      evaluation: rawResult.advantages.evaluation,
      category: '个人优势'
    });
  }
  
  // 编程评估
  if (rawResult.code && rawResult.code.evaluation) {
    detailedEvaluations.push({
      question: rawResult.code.question,
      userAnswer: rawResult.code.user_answer,
      referenceAnswer: rawResult.code.reference_answer,
      evaluation: rawResult.code.evaluation,
      category: '编程能力'
    });
  }

  return {
    overallScore,
    categoriesScore,
    strengths: strengths.length > 0 ? strengths : ['暂无明显优势'],
    improvements: improvements.length > 0 ? improvements : ['需要全面提升'],
    suggestions: '建议在项目描述中多展示技术难点和解决方案',
    detailedEvaluations
  };
};

export default function Home() {
  const [step, setStep] = useState<'upload' | 'interview' | 'evaluating' | 'result'>('upload');
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [assessmentResult, setAssessmentResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);

  const handleFileAccepted = (file: File) => {
    setFile(file);
  };

  const handleAnalyzeClick = async () => {
    if (!file) {
      setError('请先上传简历文件');
      return;
    }
    try {
      const data = await uploadResume(file);
      setResumeData(data);
      setStep('interview');
    } catch (err) {
      setError(err instanceof Error ? err.message : '上传失败');
    }
  };

  const handleInterviewComplete = async (answers: AnswerData[]) => {
    try {
      setStep('evaluating'); // 立即切换到评估状态
      const result = await evaluateInterview(answers);
      setAssessmentResult(result);
      setStep('result');
    } catch (err) {
      setError(err instanceof Error ? err.message : '评估失败');
      setStep('interview'); // 如果评估失败，回到面试页面
    }
  };

  const handleRestart = () => {
    setStep('upload');
    setResumeData(null);
    setAssessmentResult(null);
    setError(null);
    setFile(null);
  };

  return (
    <main className="min-h-screen bg-slate-50 py-12">
      <div className="container mx-auto px-4">
        {error && (
          <div className="mb-8 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
      </div>
        )}



        {step === 'upload' && (
      <ResumeUpload 
        onFileAccepted={handleFileAccepted}
        onAnalyzeClick={handleAnalyzeClick}
      />
        )}

        {step === 'interview' && resumeData && resumeData.questions && Array.isArray(resumeData.questions.projects) && (
          <InterviewQuestions
            questions={resumeData.questions.projects.map((q: any, index: number) => ({
              id: `project_${index}`,
              category: '项目经历',
              question: q.question,
              hasFollowUp: false
            })).concat([
              ...(resumeData.questions.advantages && resumeData.questions.advantages.question ? [{
                id: 'advantage_1',
                category: '个人优势',
                question: resumeData.questions.advantages.question,
                hasFollowUp: false
              }] : []),
              ...(resumeData.questions.code && Array.isArray(resumeData.questions.code) && resumeData.questions.code.length > 0 ? [{
                id: 'code_1',
                category: '编程能力',
                question: resumeData.questions.code[0],
                hasFollowUp: false
              }] : [])
            ])}
            onComplete={handleInterviewComplete}
          />
        )}

        {step === 'evaluating' && (
          <div className="w-full max-w-2xl mx-auto">
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-8 text-center">
              <div className="mb-6">
                <div className="w-16 h-16 mx-auto mb-4 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
                <h2 className="text-2xl font-semibold text-slate-800 mb-2">正在评估您的回答</h2>
                <p className="text-slate-600">
                  AI正在分析您的面试表现，生成详细的评估报告...
                </p>
              </div>
              <div className="space-y-2 text-sm text-slate-500">
                <p>• 分析回答质量和技术深度</p>
                <p>• 评估表达能力和逻辑思维</p>
                <p>• 生成个性化改进建议</p>
        </div>
      </div>
    </div>
        )}

        {step === 'result' && assessmentResult && (
          <AssessmentResult
            result={processAssessmentResult(assessmentResult) || {
              overallScore: 60,
              categoriesScore: {
                '技术深度': 60,
                '表达能力': 60,
                '项目理解': 60,
                '问题解决能力': 60
              },
              strengths: ['暂无评估数据'],
              improvements: ['请确保回答完整性'],
              suggestions: '建议提供更详细的回答',
              detailedEvaluations: []
            }}
            onRestart={handleRestart}
          />
        )}
      </div>
    </main>
  );
} 
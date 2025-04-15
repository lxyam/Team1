import React from 'react';
import { Check, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface CategoryScore {
  [key: string]: number;
}

interface AssessmentResultProps {
  result: {
    overallScore: number;
    categoriesScore: CategoryScore;
    strengths: string[];
    improvements: string[];
    suggestions: string;
  };
  onRestart: () => void;
}

export function AssessmentResult({ result, onRestart }: AssessmentResultProps) {
  const { overallScore, categoriesScore, strengths, improvements, suggestions } = result;
  
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-primary-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };
  
  const getScoreBackground = (score: number) => {
    if (score >= 90) return 'bg-green-100';
    if (score >= 80) return 'bg-primary-100';
    if (score >= 70) return 'bg-yellow-100';
    return 'bg-red-100';
  };
  
  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-8">
        <h2 className="text-2xl font-bold text-slate-800 mb-2">简历答题分析结果</h2>
        <p className="text-slate-600 mb-8">
          基于您的简历内容和问答表现，以下是我们的综合评估和建议
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div className="bg-slate-50 p-6 rounded-lg text-center">
            <div className="text-5xl font-bold mb-2 text-primary-600">{overallScore}</div>
            <div className="text-slate-600">总体得分</div>
          </div>
          
          <div className="md:col-span-2">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">分项得分</h3>
            <div className="space-y-3">
              {Object.entries(categoriesScore).map(([category, score]) => (
                <div key={category} className="flex items-center">
                  <div className="w-32 text-slate-700">{category}</div>
                  <div className="flex-1">
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full bg-primary-600" 
                        style={{ width: `${score}%` }}
                      />
                    </div>
                  </div>
                  <div className={`w-12 font-medium text-right ${getScoreColor(score)}`}>
                    {score}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div>
            <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center">
              <Check className="h-5 w-5 text-green-500 mr-2" />
              优势
            </h3>
            <ul className="space-y-2">
              {strengths.map((strength, index) => (
                <li key={index} className="flex">
                  <span className="mr-2 text-green-500">•</span>
                  <span className="text-slate-700">{strength}</span>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center">
              <AlertCircle className="h-5 w-5 text-yellow-500 mr-2" />
              改进空间
            </h3>
            <ul className="space-y-2">
              {improvements.map((improvement, index) => (
                <li key={index} className="flex">
                  <span className="mr-2 text-yellow-500">•</span>
                  <span className="text-slate-700">{improvement}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
        
        <div className="border-t border-slate-200 pt-6 mb-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">建议与下一步</h3>
          <p className="text-slate-700 bg-slate-50 p-4 rounded-lg italic">
            "{suggestions}"
          </p>
        </div>
        
        <div className="flex justify-center">
          <Button onClick={onRestart}>
            重新开始分析
          </Button>
        </div>
      </div>
    </div>
  );
} 
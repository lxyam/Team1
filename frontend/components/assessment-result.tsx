import React, { useState } from 'react';
import { Check, AlertCircle, ChevronDown, ChevronUp, MessageCircle, User, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface CategoryScore {
  [key: string]: number;
}

interface QuestionEvaluation {
  question: string;
  userAnswer: string;
  referenceAnswer: string;
  evaluation: {
    [key: string]: {
      评分: string;
      理由: string;
    };
  };
  category: string;
}

interface AssessmentResultProps {
  result: {
    overallScore: number;
    categoriesScore: CategoryScore;
    strengths: string[];
    improvements: string[];
    suggestions: string;
    detailedEvaluations?: QuestionEvaluation[];
  };
  onRestart: () => void;
}

export function AssessmentResult({ result, onRestart }: AssessmentResultProps) {
  const { overallScore, categoriesScore, strengths, improvements, suggestions, detailedEvaluations } = result;
  const [expandedQuestions, setExpandedQuestions] = useState<Set<number>>(new Set());
  
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-primary-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };
  
  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'text-green-600 bg-green-100';
      case 'B': return 'text-blue-600 bg-blue-100';
      case 'C': return 'text-yellow-600 bg-yellow-100';
      case 'D': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };
  
  const toggleQuestion = (index: number) => {
    const newExpanded = new Set(expandedQuestions);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedQuestions(newExpanded);
  };
  
  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* 总体评分概览 */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h2 className="text-2xl font-bold text-slate-800 mb-2">面试评估报告</h2>
        <p className="text-slate-600 mb-6">
          基于您的简历内容和问答表现，以下是详细的评估结果
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-50 p-6 rounded-lg text-center">
            <div className={`text-5xl font-bold mb-2 ${getScoreColor(overallScore)}`}>{overallScore}</div>
            <div className="text-slate-600">总体得分</div>
          </div>
          
          <div className="md:col-span-2">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">分项得分</h3>
            <div className="space-y-3">
              {Object.entries(categoriesScore).map(([category, score]) => (
                <div key={category} className="flex items-center">
                  <div className="w-32 text-slate-700">{category}</div>
                  <div className="flex-1 mx-4">
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
      </div>

      {/* 详细问题评估 */}
      {detailedEvaluations && detailedEvaluations.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
          <h3 className="text-xl font-semibold text-slate-800 mb-4">详细问题评估</h3>
          <div className="space-y-4">
            {detailedEvaluations.map((evaluation, index) => (
              <div key={index} className="border border-slate-200 rounded-lg overflow-hidden">
                <div 
                  className="p-4 bg-slate-50 cursor-pointer hover:bg-slate-100 transition-colors"
                  onClick={() => toggleQuestion(index)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded">
                        {evaluation.category}
                      </span>
                      <span className="font-medium text-slate-800">问题 {index + 1}</span>
                    </div>
                    {expandedQuestions.has(index) ? (
                      <ChevronUp className="h-5 w-5 text-slate-500" />
                    ) : (
                      <ChevronDown className="h-5 w-5 text-slate-500" />
                    )}
                  </div>
                </div>
                
                {expandedQuestions.has(index) && (
                  <div className="p-6 space-y-6">
                    {/* 问题 */}
                    <div className="flex items-start space-x-3">
                      <MessageCircle className="h-5 w-5 text-primary-600 mt-1 flex-shrink-0" />
                      <div>
                        <h4 className="font-medium text-slate-800 mb-2">面试问题</h4>
                        <p className="text-slate-700 bg-primary-50 p-3 rounded-lg">{evaluation.question}</p>
                      </div>
                    </div>

                    {/* 用户回答 */}
                    <div className="flex items-start space-x-3">
                      <User className="h-5 w-5 text-slate-600 mt-1 flex-shrink-0" />
                      <div>
                        <h4 className="font-medium text-slate-800 mb-2">您的回答</h4>
                        <p className="text-slate-700 bg-slate-50 p-3 rounded-lg">{evaluation.userAnswer}</p>
                      </div>
                    </div>

                    {/* 参考答案 */}
                    <div className="flex items-start space-x-3">
                      <BookOpen className="h-5 w-5 text-green-600 mt-1 flex-shrink-0" />
                      <div>
                        <h4 className="font-medium text-slate-800 mb-2">参考答案</h4>
                        <div className="text-slate-700 bg-green-50 p-3 rounded-lg whitespace-pre-wrap">{evaluation.referenceAnswer}</div>
                      </div>
                    </div>

                    {/* 评估结果 */}
                    <div className="border-t pt-4">
                      <h4 className="font-medium text-slate-800 mb-3">评估结果</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {Object.entries(evaluation.evaluation).map(([dimension, result]) => (
                          <div key={dimension} className="border border-slate-200 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-medium text-slate-700">{dimension}</span>
                              <span className={`px-2 py-1 text-xs font-bold rounded ${getGradeColor(result.评分)}`}>
                                {result.评分}
                              </span>
                            </div>
                            <p className="text-sm text-slate-600">{result.理由}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 总结和建议 */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-xl font-semibold text-slate-800 mb-6">总结与建议</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <h4 className="text-lg font-semibold text-slate-800 mb-3 flex items-center">
              <Check className="h-5 w-5 text-green-500 mr-2" />
              表现优势
            </h4>
            <ul className="space-y-2">
              {strengths.map((strength, index) => (
                <li key={index} className="flex items-start">
                  <span className="mr-2 text-green-500 mt-1">•</span>
                  <span className="text-slate-700">{strength}</span>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4 className="text-lg font-semibold text-slate-800 mb-3 flex items-center">
              <AlertCircle className="h-5 w-5 text-yellow-500 mr-2" />
              改进方向
            </h4>
            <ul className="space-y-2">
              {improvements.map((improvement, index) => {
                // 检查是否是重复的内容
                const isDuplicate = improvements.findIndex(item => 
                  item.split(':')[0] === improvement.split(':')[0] && 
                  index > improvements.findIndex(i => i.split(':')[0] === item.split(':')[0])
                ) !== -1;
                
                if (!isDuplicate) {
                  return (
                    <li key={index} className="flex items-start">
                      <span className="mr-2 text-yellow-500 mt-1">•</span>
                      <span className="text-slate-700">{improvement}</span>
                    </li>
                  );
                }
                return null;
              })}
            </ul>
          </div>
        </div>
        
        <div className="border-t border-slate-200 pt-6 mb-6">
          <h4 className="text-lg font-semibold text-slate-800 mb-3">专业建议</h4>
          <p className="text-slate-700 bg-slate-50 p-4 rounded-lg">
            {suggestions}
          </p>
        </div>
        
        <div className="flex justify-center">
          <Button onClick={onRestart} size="lg">
            重新开始分析
          </Button>
        </div>
      </div>
    </div>
  );
} 
import React, { useState } from 'react';
import { ChevronRight, MessageCircle, Send, User, CornerDownRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface Question {
  id: string;
  category: string;
  question: string;
  hasFollowUp: boolean;
  followUpQuestions?: Array<{
    id: string;
    question: string;
  }>;
}

interface AnswerData {
  questionId: string;
  answer: string;
  isFollowUp?: boolean;
  parentQuestionId?: string; // 追问对应的原问题ID
}

interface InterviewQuestionsProps {
  questions: Question[];
  onComplete: (answers: AnswerData[]) => void;
}

export function InterviewQuestions({ questions, onComplete }: InterviewQuestionsProps) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showFollowUp, setShowFollowUp] = useState(false);
  const [answers, setAnswers] = useState<AnswerData[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const currentQuestion = questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  const followUpQuestion = currentQuestion?.hasFollowUp && currentQuestion.followUpQuestions?.[0];
  
  const handleAnswerSubmit = () => {
    if (currentAnswer.trim() === '') return;
    
    const newAnswer: AnswerData = {
      questionId: showFollowUp && followUpQuestion 
        ? followUpQuestion.id 
        : currentQuestion.id,
      answer: currentAnswer,
      isFollowUp: showFollowUp,
      parentQuestionId: showFollowUp ? currentQuestion.id : undefined
    };
    
    setAnswers([...answers, newAnswer]);
    setCurrentAnswer('');
    
    if (showFollowUp) {
      // If we just answered a follow-up, move to the next question
      setShowFollowUp(false);
      if (!isLastQuestion) {
        setCurrentQuestionIndex(prev => prev + 1);
      } else {
        // All questions completed including follow-ups
        setIsSubmitting(true);
        onComplete([...answers, newAnswer]);
      }
    } else if (currentQuestion.hasFollowUp && followUpQuestion) {
      // Show follow-up if the current question has one
      setShowFollowUp(true);
    } else if (!isLastQuestion) {
      // No follow-up, go to next question
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      // All questions completed
      setIsSubmitting(true);
      onComplete([...answers, newAnswer]);
    }
  };
  
  // Use Array.from instead of Set to avoid TypeScript error
  const categories = Array.from(new Set(questions.map(q => q.category)));
  const progress = Math.round(
    ((currentQuestionIndex + (showFollowUp ? 0.5 : 0)) / questions.length) * 100
  );

  // 根据问题ID找到对应的问题
  const findQuestionById = (id: string) => {
    for (const q of questions) {
      if (q.id === id) return q;
      if (q.followUpQuestions) {
        const followUp = q.followUpQuestions.find(fq => fq.id === id);
        if (followUp) return followUp;
      }
    }
    return null;
  };
  
  // 组织问答记录为会话组，将追问和回答与原问题关联
  const organizeQuestionsAndAnswers = () => {
    const result: {
      type: 'original' | 'followup';
      questionId: string;
      question: string | undefined;
      answer: string;
      parentId?: string;
    }[] = [];
    
    const answersMap = new Map<string, string>();
    const followupAnswersMap = new Map<string, {parentId: string, answer: string}>();
    
    // 先整理所有回答
    answers.forEach(a => {
      if (a.isFollowUp && a.parentQuestionId) {
        followupAnswersMap.set(a.questionId, {
          parentId: a.parentQuestionId,
          answer: a.answer
        });
      } else {
        answersMap.set(a.questionId, a.answer);
      }
    });
    
    // 使用Array.from解决TypeScript迭代器错误
    const originalQuestions = Array.from(answersMap.entries());
    
    // 按顺序添加原始问题和回答
    for (const [qId, answer] of originalQuestions) {
      const question = findQuestionById(qId);
      result.push({
        type: 'original',
        questionId: qId,
        question: question?.question,
        answer
      });
      
      // 使用Array.from解决TypeScript迭代器错误
      const followupQuestions = Array.from(followupAnswersMap.entries());
      
      // 查找并添加对应的追问和回答
      for (const [fqId, data] of followupQuestions) {
        if (data.parentId === qId) {
          const followupQ = findQuestionById(fqId);
          result.push({
            type: 'followup',
            questionId: fqId,
            question: followupQ?.question,
            answer: data.answer,
            parentId: qId
          });
        }
      }
    }
    
    return result;
  };
  
  const conversationHistory = organizeQuestionsAndAnswers();
  
  return (
    <div className="w-full max-w-4xl mx-auto h-full flex flex-col">
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 flex-1 flex flex-col">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-slate-800 mb-2">模拟面试环节</h2>
          <p className="text-slate-600 mb-2">
            请回答以下问题，系统将模拟真实面试场景进行提问。部分问题可能会有追问，请详细回答每个问题。
          </p>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <div className="flex items-center">
              <MessageCircle className="h-4 w-4 mr-1 text-primary-600" />
              <span>面试官提问</span>
            </div>
            <div className="flex items-center ml-3">
              <CornerDownRight className="h-4 w-4 mr-1 text-secondary-600" />
              <span>面试官追问</span>
            </div>
          </div>
        </div>
        
        <div className="flex mb-6 gap-2 flex-wrap">
          {categories.map((category) => (
            <div 
              key={category}
              className={cn(
                "px-4 py-1.5 rounded-full text-sm font-medium",
                questions[currentQuestionIndex].category === category
                  ? "bg-primary-100 text-primary-800"
                  : "bg-slate-100 text-slate-600"
              )}
            >
              {category}
            </div>
          ))}
        </div>
        
        <div className="flex-1 flex flex-col">
          {/* Previous Q&A chat history - scrollable area */}
          <div className="flex-1 overflow-y-auto mb-4 space-y-6">
            {conversationHistory.map((item, idx) => (
              <div key={idx} className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
                    {item.type === 'original' ? (
                      <MessageCircle className="h-5 w-5 text-primary-600" />
                    ) : (
                      <CornerDownRight className="h-5 w-5 text-secondary-600" />
                    )}
                  </div>
                  <div className={cn(
                    "flex-1 rounded-lg p-4 text-slate-800",
                    item.type === 'original' 
                      ? "bg-slate-100" 
                      : "bg-secondary-50 border-l-4 border-secondary-200 ml-6"
                  )}>
                    {item.question}
                    {item.type === 'followup' && (
                      <div className="text-xs text-secondary-600 mt-1">
                        追问
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">
                    <User className="h-5 w-5 text-slate-600" />
                  </div>
                  <div className={cn(
                    "flex-1 bg-slate-50 rounded-lg p-4 text-slate-800",
                    item.type === 'followup' && "ml-6"
                  )}>
                    {item.answer}
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Fixed current question and answer area - always visible at bottom */}
          <div className="border-t pt-4">
            <div className="mb-4 w-full bg-slate-200 rounded-full h-2">
              <div 
                className="bg-primary-600 h-2 rounded-full" 
                style={{ width: `${progress}%` }}
              />
            </div>
            
            {/* Current question */}
            <div className="mb-4 flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
                {showFollowUp ? (
                  <CornerDownRight className="h-5 w-5 text-secondary-600" />
                ) : (
                  <MessageCircle className="h-5 w-5 text-primary-600" />
                )}
              </div>
              <div className={cn(
                "flex-1 rounded-lg p-4 text-slate-800 font-medium",
                showFollowUp 
                  ? "bg-secondary-50 border-l-4 border-secondary-200" 
                  : "bg-slate-100"
              )}>
                {showFollowUp && followUpQuestion
                  ? followUpQuestion.question
                  : currentQuestion.question}
                
                {showFollowUp && (
                  <div className="text-xs text-secondary-600 mt-1">
                    追问
                  </div>
                )}
              </div>
            </div>
            
            {/* Answer input */}
            <div className="flex gap-3">
              <textarea
                value={currentAnswer}
                onChange={(e) => setCurrentAnswer(e.target.value)}
                className="flex-1 rounded-md border-slate-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 min-h-[120px] p-3 resize-none"
                placeholder="请在此处输入您的回答..."
                disabled={isSubmitting}
              />
              <Button 
                onClick={handleAnswerSubmit}
                className="self-end"
                disabled={currentAnswer.trim() === '' || isSubmitting}
              >
                {isSubmitting ? (
                  <span className="h-4 w-4 animate-spin rounded-full border-t-2 border-white"></span>
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 
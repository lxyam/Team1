import React, { useState } from 'react';
import { Button } from '@/components/ui/button';

interface SupplementaryInfoProps {
  resumeEvaluation: {
    issues: Array<{
      id: string;
      area: string;
      description: string;
    }>;
  };
  onSubmit: (supplements: Record<string, string>) => void;
}

export function SupplementaryInfo({ resumeEvaluation, onSubmit }: SupplementaryInfoProps) {
  const [supplements, setSupplements] = useState<Record<string, string>>({});
  const [activeTab, setActiveTab] = useState<string | null>(
    resumeEvaluation.issues.length > 0 ? resumeEvaluation.issues[0].area : null
  );
  
  const handleInputChange = (issueId: string, value: string) => {
    setSupplements(prev => ({
      ...prev,
      [issueId]: value
    }));
  };
  
  const handleSubmit = () => {
    onSubmit(supplements);
  };
  
  // Group issues by area
  const issuesByArea = resumeEvaluation.issues.reduce<Record<string, typeof resumeEvaluation.issues>>(
    (acc, issue) => {
      if (!acc[issue.area]) {
        acc[issue.area] = [];
      }
      acc[issue.area].push(issue);
      return acc;
    },
    {}
  );
  
  const areas = Object.keys(issuesByArea);
  
  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-8">
        <h2 className="text-xl font-semibold text-slate-800 mb-6">补充信息</h2>
        
        <div className="mb-6">
          <p className="text-slate-600 mb-4">
            基于对您简历的分析，我们发现以下几个方面可能需要补充说明。请在相应区域添加更多详细信息，以便系统能更全面地评估您的简历。
          </p>
          
          {areas.length === 0 ? (
            <div className="p-4 bg-green-50 text-green-700 rounded-md">
              您的简历已经很完善，无需补充更多信息。
            </div>
          ) : (
            <>
              <div className="border-b border-slate-200">
                <nav className="flex space-x-2 overflow-x-auto">
                  {areas.map(area => (
                    <button
                      key={area}
                      onClick={() => setActiveTab(area)}
                      className={`py-2 px-4 font-medium text-sm whitespace-nowrap transition-colors ${
                        activeTab === area
                          ? 'border-b-2 border-primary-600 text-primary-600'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      {area}
                    </button>
                  ))}
                </nav>
              </div>
              
              <div className="mt-6 space-y-8">
                {activeTab && issuesByArea[activeTab]?.map(issue => (
                  <div key={issue.id} className="space-y-3">
                    <label className="block font-medium text-slate-700">
                      {issue.description}
                    </label>
                    <textarea
                      value={supplements[issue.id] || ''}
                      onChange={e => handleInputChange(issue.id, e.target.value)}
                      className="w-full rounded-md border-slate-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 min-h-[120px] p-3"
                      placeholder="请在此处补充相关信息..."
                    />
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
        
        <div className="flex justify-between mt-8">
          <Button variant="outline" onClick={() => window.history.back()}>
            返回
          </Button>
          <Button onClick={handleSubmit}>
            提交并继续
          </Button>
        </div>
      </div>
    </div>
  );
} 
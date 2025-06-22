const API_BASE_URL = 'http://localhost:8000/api';

export interface ResumeData {
  resume: any;
  questions: {
    projects: any[];
    advantages: any;
    code: any;
  };
}

export interface AnswerData {
  questionId: string;
  answer: string;
  isFollowUp?: boolean;
  parentQuestionId?: string;
}

export async function uploadResume(file: File): Promise<ResumeData> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/resume/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('简历上传失败');
  }

  return response.json();
}

export async function evaluateInterview(answers: AnswerData[]): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/interview/evaluate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(answers),
  });

  if (!response.ok) {
    throw new Error('评估失败');
  }

  return response.json();
} 
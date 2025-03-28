import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import { useParams } from 'react-router-dom';
import axios from 'axios';

interface Answer {
  answer: string;
  score: number;
  feedback: string;
  sub_question_index?: number;
}

interface Question {
  id: string;
  question: string;
  subQuestions?: string[];
  answers: Answer[];
}

interface Section {
  project: Question[];
  advantage: Question[];
  coding: Question[];
}

interface Report {
  resume: any;
  sections: Section;
  overall_score: number;
  section_scores: {
    project: number;
    advantage: number;
    coding: number;
  };
}

const sectionTitles = {
  project: '项目经验',
  advantage: '个人优势',
  coding: '编程能力'
};

const Results: React.FC = () => {
  const { interviewId } = useParams<{ interviewId: string }>();
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/interviews/${interviewId}/report`);
        setReport(response.data);
      } catch (err) {
        console.error('Error fetching report:', err);
        setError('获取面试报告失败');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [interviewId]);

  if (loading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error || !report) {
    return (
      <Container>
        <Alert severity="error">{error || '无法加载面试报告'}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 3, mt: 4 }}>
        <Typography variant="h4" gutterBottom align="center">
          面试评估报告
        </Typography>

        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            总体评分：{Math.round(report.overall_score)}分
          </Typography>
          <Divider sx={{ my: 2 }} />
          
          {Object.entries(sectionTitles).map(([type, title]) => (
            <Box key={type} sx={{ mb: 4 }}>
              <Typography variant="h5" gutterBottom>
                {title}部分（{Math.round(report.section_scores[type as keyof Section])}分）
              </Typography>
              
              {report.sections[type as keyof Section].map((question, qIndex) => (
                <Card key={question.id} variant="outlined" sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      第 {qIndex + 1} 题：{question.question}
                    </Typography>

                    {question.subQuestions ? (
                      question.subQuestions.map((subQ, subIndex) => {
                        const answer = question.answers.find(a => a.sub_question_index === subIndex);
                        return (
                          <Box key={`${question.id}-${subIndex}`} sx={{ mb: 2 }}>
                            <Typography variant="subtitle1" gutterBottom>
                              子问题 {subIndex + 1}：{subQ}
                            </Typography>
                            <Typography variant="body1" sx={{ mb: 1 }}>
                              答案：{answer?.answer || '未作答'}
                            </Typography>
                            {answer && (
                              <>
                                <Typography variant="body2" color="primary">
                                  得分：{answer.score}分
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  评价：{answer.feedback}
                                </Typography>
                              </>
                            )}
                          </Box>
                        );
                      })
                    ) : (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body1" sx={{ mb: 1 }}>
                          答案：{question.answers[0]?.answer || '未作答'}
                        </Typography>
                        {question.answers[0] && (
                          <>
                            <Typography variant="body2" color="primary">
                              得分：{question.answers[0].score}分
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              评价：{question.answers[0].feedback}
                            </Typography>
                          </>
                        )}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              ))}
            </Box>
          ))}
        </Box>
      </Paper>
    </Container>
  );
};

export default Results; 
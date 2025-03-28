import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  TextField,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  ButtonGroup,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Editor from '@monaco-editor/react';

interface Question {
  id: string;
  type: 'project' | 'advantage' | 'coding';
  question: string;
  subQuestions?: string[];
  reference_answer: string;
  difficulty: string;
  points: number;
}

interface QuestionsByType {
  project: Question[];
  advantage: Question[];
  coding: Question[];
}

interface AnswerToSubmit {
  question_id: string;
  sub_question_index?: number;
  answer: string;
}

const Interview: React.FC = () => {
  const { interviewId } = useParams<{ interviewId: string }>();
  const navigate = useNavigate();
  const [currentType, setCurrentType] = useState<'project' | 'advantage' | 'coding'>('project');
  const [timeLeft, setTimeLeft] = useState(7200); // 2小时 = 7200秒
  
  // 将 sectionTitles 移到这里
  const sectionTitles = {
    project: '项目经验问题',
    advantage: '个人优势问题',
    coding: '编程能力问题'
  };

  const [questions, setQuestions] = useState<QuestionsByType>({
    project: [],
    advantage: [],
    coding: []
  });
  const [answers, setAnswers] = useState<{
    project: Record<string, string>;
    advantage: Record<string, string>;
    coding: Record<string, string>;
  }>({
    project: {},
    advantage: {},
    coding: {}
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingStatus, setLoadingStatus] = useState('正在准备面试问题...');
  const [submitProgress, setSubmitProgress] = useState(0);
  const [submitStatus, setSubmitStatus] = useState('');

  // 平滑更新进度
  const updateProgressSmoothly = (targetProgress: number, status?: string) => {
    const step = 0.5;
    const interval = 50;

    if (status) {
      setLoadingStatus(status);
    }

    setLoadingProgress(targetProgress);
  };

  // 平滑更新提交进度
  const updateSubmitProgress = (targetProgress: number, status?: string) => {
    const step = 0.5;
    const interval = 50;

    if (status) {
      setSubmitStatus(status);
    }

    const smoothProgress = (currentProgress: number) => {
      if (currentProgress < targetProgress) {
        const nextProgress = Math.min(currentProgress + step, targetProgress);
        setSubmitProgress(nextProgress);
        setTimeout(() => smoothProgress(nextProgress), interval);
      }
    };

    smoothProgress(submitProgress);
  };

  // 倒计时逻辑
  useEffect(() => {
    if (timeLeft <= 0) {
      // 时间到，自动提交
      handleSubmitAll();
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft(prev => prev - 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft]);

  // 格式化时间
  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // 自动提交所有答案
  const handleSubmitAll = async () => {
    try {
      // TODO: 实现自动提交逻辑
      navigate(`/results/${interviewId}`);
    } catch (err) {
      setError('提交失败，请重试');
    }
  };

  // 一次性获取所有问题
  useEffect(() => {
    const fetchAllQuestions = async () => {
      if (!interviewId) return;
      
      try {
        setLoading(true);
        setLoadingProgress(0);
        setLoadingStatus('正在准备面试问题...');

        const types = ['project', 'advantage', 'coding'];
        const counts = { project: 4, advantage: 3, coding: 4 };  // 每个部分的主问题数量
        const allQuestions: QuestionsByType = {
          project: [],
          advantage: [],
          coding: []
        };

        for (let i = 0; i < types.length; i++) {
          const type = types[i] as keyof QuestionsByType;
          updateProgressSmoothly((i * 33), `正在生成${sectionTitles[type]}...`);
          
          const response = await axios.get(`http://localhost:8000/api/interviews/${interviewId}/questions`, {
            params: {
              type: type,
              count: counts[type]
            }
          });
          
          allQuestions[type] = response.data;
        }

        setQuestions(allQuestions);
        updateProgressSmoothly(100, '准备就绪');
        
        // 等待进度条动画完成后显示问题
        setTimeout(() => {
          setLoading(false);
        }, 1000);
      } catch (err) {
        console.error('Error fetching questions:', err);
        setError('加载问题失败，请刷新页面重试');
        setLoading(false);
      }
    };

    fetchAllQuestions();
  }, [interviewId]);

  const handleAnswerChange = (questionId: string, subIndex: number | undefined, value: string) => {
    const answerKey = subIndex !== undefined ? `${questionId}-${subIndex}` : questionId;
    setAnswers(prev => ({
      ...prev,
      [currentType]: {
        ...prev[currentType],
        [answerKey]: value
      }
    }));
  };

  const getAnswer = (questionId: string, subIndex: number | undefined) => {
    const answerKey = subIndex !== undefined ? `${questionId}-${subIndex}` : questionId;
    return answers[currentType][answerKey] || '';
  };

  // 检查当前部分是否已完成
  const isCurrentSectionComplete = () => {
    const currentQuestions = questions[currentType] || [];
    return currentQuestions.every(question => 
      question.subQuestions?.every((_, index) => {
        const answer = getAnswer(question.id, index);
        return answer && answer.trim().length > 0;
      }) ?? true
    );
  };

  // 切换到下一部分
  const handleNext = () => {
    if (currentType === 'project') {
      setCurrentType('advantage');
    } else if (currentType === 'advantage') {
      setCurrentType('coding');
    }
  };

  // 返回上一部分
  const handleBack = () => {
    if (currentType === 'advantage') {
      setCurrentType('project');
    } else if (currentType === 'coding') {
      setCurrentType('advantage');
    }
  };

  // 提交所有答案
  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      setConfirmDialogOpen(false);
      
      // 收集所有答案
      updateSubmitProgress(20, '正在整理答案...');
      const answersToSubmit: AnswerToSubmit[] = [];
      
      for (const type of ['project', 'advantage', 'coding'] as const) {
        for (const question of questions[type]) {
          if (question.subQuestions) {
            question.subQuestions.forEach((_, index) => {
              const answerKey = `${question.id}-${index}`;
              const answer = answers[type][answerKey];
              if (answer && answer.trim()) {
                answersToSubmit.push({
                  question_id: question.id,
                  sub_question_index: index,
                  answer: answer
                });
              }
            });
          }
        }
      }

      // 提交所有答案
      updateSubmitProgress(40, '正在提交答案...');
      await Promise.all(
        answersToSubmit.map(answer => 
          axios.post(`http://localhost:8000/api/interviews/${interviewId}/answers`, answer)
        )
      );

      // 等待评估完成
      updateSubmitProgress(60, '正在评估答案...');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      updateSubmitProgress(80, '正在生成报告...');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      updateSubmitProgress(100, '评估完成');
      
      // 等待进度条动画完成后跳转
      setTimeout(() => {
        navigate(`/results/${interviewId}`);
      }, 1000);
    } catch (err) {
      console.error('Error submitting answers:', err);
      setError('提交答案失败');
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="sm">
        <Box 
          display="flex" 
          flexDirection="column" 
          alignItems="center" 
          justifyContent="center" 
          minHeight="100vh"
          textAlign="center"
        >
          <Typography variant="h6" gutterBottom>
            {loadingStatus}
          </Typography>
          <Box sx={{ width: '100%', mt: 2 }}>
            <LinearProgress 
              variant="determinate" 
              value={loadingProgress} 
              sx={{ height: 8, borderRadius: 4 }}
            />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {Math.round(loadingProgress)}%
            </Typography>
          </Box>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>
      </Container>
    );
  }

  const currentQuestions = questions[currentType] || [];

  return (
    <Container maxWidth="md">
      {/* 添加倒计时显示 */}
      <Box sx={{ 
        position: 'fixed', 
        top: 20, 
        right: 20, 
        zIndex: 1000,
        backgroundColor: timeLeft <= 300 ? '#ff4444' : '#ffffff',
        padding: 2,
        borderRadius: 2,
        boxShadow: 2,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <Typography variant="h6" color={timeLeft <= 300 ? 'white' : 'text.primary'}>
          剩余时间
        </Typography>
        <Typography variant="h4" color={timeLeft <= 300 ? 'white' : 'text.primary'}>
          {formatTime(timeLeft)}
        </Typography>
      </Box>

      <Paper sx={{ p: 3, mt: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5">
            {sectionTitles[currentType]}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {currentType === 'project' ? '第一部分' : 
             currentType === 'advantage' ? '第二部分' : '第三部分'}
          </Typography>
        </Box>

        <Box sx={{ mb: 4 }}>
          {currentQuestions.map((question, questionIndex) => (
            <Card key={question.id} variant="outlined" sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  第 {questionIndex + 1} 题：{question.question}
                </Typography>

                {currentType !== 'coding' ? (
                  question.subQuestions?.map((subQuestion, subIndex) => (
                    <Box key={`${question.id}-${subIndex}`} sx={{ mb: 3 }}>
                      <Typography variant="subtitle1" gutterBottom>
                        子问题 {subIndex + 1}：{subQuestion}
                      </Typography>
                      <TextField
                        fullWidth
                        multiline
                        rows={4}
                        variant="outlined"
                        value={getAnswer(question.id, subIndex)}
                        onChange={(e) => handleAnswerChange(question.id, subIndex, e.target.value)}
                        placeholder="请输入您的答案..."
                        sx={{ mt: 1 }}
                      />
                    </Box>
                  ))
                ) : (
                  <TextField
                    fullWidth
                    multiline
                    rows={8}
                    variant="outlined"
                    value={getAnswer(question.id, undefined)}
                    onChange={(e) => handleAnswerChange(question.id, undefined, e.target.value)}
                    placeholder="请输入您的答案..."
                    sx={{ mt: 2 }}
                  />
                )}
              </CardContent>
            </Card>
          ))}
        </Box>

        <Box display="flex" justifyContent="flex-end">
          <ButtonGroup>
            {currentType !== 'project' && (
              <Button
                variant="outlined"
                onClick={handleBack}
              >
                返回上一部分
              </Button>
            )}
            {currentType !== 'coding' ? (
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={!isCurrentSectionComplete()}
              >
                进入下一部分
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={() => setConfirmDialogOpen(true)}
                disabled={submitting || !isCurrentSectionComplete()}
              >
                {submitting ? <CircularProgress size={24} /> : '完成面试'}
              </Button>
            )}
          </ButtonGroup>
        </Box>
      </Paper>

      <Dialog 
        open={submitting} 
        fullWidth 
        maxWidth="sm"
        PaperProps={{
          style: {
            minHeight: '200px',
          },
        }}
      >
        <DialogTitle>提交进度</DialogTitle>
        <DialogContent>
          <Box 
            display="flex" 
            flexDirection="column" 
            alignItems="center" 
            justifyContent="center"
            minHeight="120px"
          >
            <Typography variant="h6" gutterBottom>
              {submitStatus}
            </Typography>
            <Box sx={{ width: '100%', mt: 2 }}>
              <LinearProgress 
                variant="determinate" 
                value={submitProgress} 
                sx={{ height: 8, borderRadius: 4 }}
              />
              <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
                {Math.round(submitProgress)}%
              </Typography>
            </Box>
          </Box>
        </DialogContent>
      </Dialog>

      <Dialog open={confirmDialogOpen} onClose={() => setConfirmDialogOpen(false)}>
        <DialogTitle>确认提交</DialogTitle>
        <DialogContent>
          <Typography>
            您确定要完成面试吗？提交后将无法修改任何答案。
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialogOpen(false)}>继续作答</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            确认提交
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Interview; 
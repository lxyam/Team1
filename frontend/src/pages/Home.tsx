import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // 检查文件类型
    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!validTypes.includes(file.type)) {
      setError('请上传 PDF 或 Word 文档');
      return;
    }

    // 检查文件大小（最大 10MB）
    if (file.size > 10 * 1024 * 1024) {
      setError('文件大小不能超过 10MB');
      return;
    }

    await uploadFile(file);
  };

  const uploadFile = async (file: File) => {
    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('resume', file);

    try {
      const response = await axios.post(
        'http://localhost:8000/api/interviews/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        }
      );

      if (response.data.interview_id) {
        navigate(`/interview/${response.data.interview_id}`);
      } else {
        throw new Error('未收到面试ID');
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError('上传失败，请重试');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Paper sx={{ p: 4, mt: 8, textAlign: 'center' }}>
        <Typography variant="h5" gutterBottom>
          AI 面试助手
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          上传您的简历，开始智能面试
        </Typography>

        <Box sx={{ mt: 3 }}>
          <input
            accept=".pdf,.doc,.docx"
            style={{ display: 'none' }}
            id="resume-file"
            type="file"
            onChange={handleFileChange}
            disabled={uploading}
          />
          <label htmlFor="resume-file">
            <Button
              variant="contained"
              component="span"
              disabled={uploading}
              sx={{ minWidth: 120 }}
            >
              {uploading ? '请稍候...' : '开始面试'}
            </Button>
          </label>
        </Box>

        {error && (
          <Alert 
            severity="error" 
            sx={{ mt: 2 }} 
            onClose={() => setError(null)}
          >
            {error}
          </Alert>
        )}
      </Paper>
    </Container>
  );
};

export default Home; 
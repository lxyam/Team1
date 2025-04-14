import React, { useState } from 'react';
import { Typography, Button, Input, Space, message } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

interface Message {
  type: 'user' | 'ai';
  content: string;
}

const CodeInterview: React.FC = () => {
  const [code, setCode] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!code.trim()) {
      message.warning('请输入代码');
      return;
    }

    setLoading(true);
    const userMessage: Message = { type: 'user', content: code };
    setMessages(prev => [...prev, userMessage]);

    try {
      if (!sessionId) {
        // 开始新的面试会话
        const startResponse = await axios.post('http://localhost:5000/interview/start', {
          name: "代码面试",
          description: "编程能力测试",
          technologies: ["Python", "JavaScript", "算法"]
        });
        
        setSessionId(startResponse.data.session_id);
        const aiMessage: Message = {
          type: 'ai',
          content: startResponse.data.question
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        // 继续面试会话
        const continueResponse = await axios.post('http://localhost:5000/interview/continue', {
          session_id: sessionId,
          answer: code
        });

        if (continueResponse.data.status === 'completed') {
          const aiMessage: Message = {
            type: 'ai',
            content: `面试结束！\n\n评估结果：\n${JSON.stringify(continueResponse.data.evaluation, null, 2)}`
          };
          setMessages(prev => [...prev, aiMessage]);
          setSessionId(null);
        } else {
          const aiMessage: Message = {
            type: 'ai',
            content: continueResponse.data.question
          };
          setMessages(prev => [...prev, aiMessage]);
        }
      }
    } catch (error) {
      message.error('提交失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="interview-container">
      <Title level={2}>代码面试</Title>
      <Paragraph>
        请编写代码解决以下问题。完成后点击提交按钮，AI 面试官会给出反馈。
      </Paragraph>

      <div className="code-editor">
        <TextArea
          value={code}
          onChange={e => setCode(e.target.value)}
          placeholder="在这里编写你的代码..."
          style={{ height: '100%', resize: 'none' }}
        />
      </div>

      <Space style={{ marginBottom: 24 }}>
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSubmit}
          loading={loading}
        >
          提交代码
        </Button>
      </Space>

      <div className="chat-container">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.type === 'user' ? 'user-message' : 'ai-message'}`}
          >
            <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{msg.content}</pre>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CodeInterview; 
import React, { useState } from 'react';
import { Typography, Input, Button, Space, message } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

interface Message {
  type: 'user' | 'ai';
  content: string;
}

const QaInterview: React.FC = () => {
  const [input, setInput] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const handleSend = async () => {
    if (!input.trim()) {
      message.warning('请输入问题');
      return;
    }

    setLoading(true);
    const userMessage: Message = { type: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      if (!sessionId) {
        // 开始新的面试会话
        const startResponse = await axios.post('http://localhost:5000/interview/start', {
          name: "问答面试",
          description: "技术问答测试",
          technologies: ["Python", "JavaScript", "Web开发"]
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
          answer: input
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
      message.error('发送失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="interview-container">
      <Title level={2}>问答面试</Title>
      <Paragraph>
        请回答 AI 面试官的问题，或提出你的问题。AI 面试官会根据你的回答给出反馈。
      </Paragraph>

      <div className="chat-container">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.type === 'user' ? 'user-message' : 'ai-message'}`}
          >
            {msg.content}
          </div>
        ))}
      </div>

      <Space.Compact style={{ width: '100%' }}>
        <TextArea
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="输入你的问题..."
          autoSize={{ minRows: 2, maxRows: 6 }}
          onPressEnter={e => {
            if (!e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={loading}
        >
          发送
        </Button>
      </Space.Compact>
    </div>
  );
};

export default QaInterview; 
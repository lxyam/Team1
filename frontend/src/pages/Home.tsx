import React from 'react';
import { Typography, Card, Row, Col, Button } from 'antd';
import { CodeOutlined, MessageOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph } = Typography;

const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="interview-container">
      <Typography>
        <Title level={1} style={{ textAlign: 'center', marginBottom: 48 }}>
          AI 面试系统
        </Title>
        <Paragraph style={{ textAlign: 'center', fontSize: 18, marginBottom: 48 }}>
          欢迎使用 AI 面试系统，这里提供代码面试和问答面试两种模式
        </Paragraph>
      </Typography>

      <Row gutter={[24, 24]} justify="center">
        <Col xs={24} sm={12} md={8}>
          <Card
            hoverable
            cover={<CodeOutlined style={{ fontSize: 48, padding: '24px' }} />}
            actions={[
              <Button type="primary" onClick={() => navigate('/code-interview')}>
                开始代码面试
              </Button>
            ]}
          >
            <Card.Meta
              title="代码面试"
              description="进行编程能力测试，包括算法题和代码实现"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card
            hoverable
            cover={<MessageOutlined style={{ fontSize: 48, padding: '24px' }} />}
            actions={[
              <Button type="primary" onClick={() => navigate('/qa-interview')}>
                开始问答面试
              </Button>
            ]}
          >
            <Card.Meta
              title="问答面试"
              description="进行技术问答，测试专业知识和沟通能力"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Home; 
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import { CodeOutlined, MessageOutlined, HomeOutlined } from '@ant-design/icons';
import Home from './pages/Home';
import CodeInterview from './pages/CodeInterview';
import QaInterview from './pages/QaInterview';
import './App.css';

const { Header, Content, Footer } = Layout;

const App: React.FC = () => {
  return (
    <Router>
      <Layout className="layout">
        <Header>
          <div className="logo" />
          <Menu theme="dark" mode="horizontal" defaultSelectedKeys={['1']}>
            <Menu.Item key="1" icon={<HomeOutlined />}>
              <a href="/">首页</a>
            </Menu.Item>
            <Menu.Item key="2" icon={<CodeOutlined />}>
              <a href="/code-interview">代码面试</a>
            </Menu.Item>
            <Menu.Item key="3" icon={<MessageOutlined />}>
              <a href="/qa-interview">问答面试</a>
            </Menu.Item>
          </Menu>
        </Header>
        <Content style={{ padding: '0 50px', marginTop: 64 }}>
          <div className="site-layout-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/code-interview" element={<CodeInterview />} />
              <Route path="/qa-interview" element={<QaInterview />} />
            </Routes>
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          AI Interview System ©{new Date().getFullYear()}
        </Footer>
      </Layout>
    </Router>
  );
};

export default App;

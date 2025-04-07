# AI驱动的简历智能问答系统

一个基于AI的智能简历智能问答系统，支持项目经验、个人优势和编程能力的综合评估。

## 项目演示

🎥 [点击观看项目演示视频](https://www.bilibili.com/video/BV1HERkYAE8D/)

## 功能特点

- 三个简历智能问答环节：项目经验、个人优势、编程能力
- 智能问题生成：基于简历内容生成针对性问题
- 实时答案评估：使用AI评估答案质量
- 计时功能：2小时答题时限
- 自动保存：实时保存答题进度
- 详细报告：生成完整的回答评估报告

## 系统架构

### 前端 (frontend/)
- 基于React + TypeScript开发
- Material-UI组件库
- 主要页面：
  - 首页：简历上传
  - 问答页：答题界面
  - 结果页：评估报告

### 后端 (backend/)
- Python + Flask框架
- 主要功能：
  - 简历解析
  - AI问题生成
  - 答案评估
  - 报告生成

## 安装说明

### 前端环境配置
```bash
cd frontend
npm install
npm start
```

### 后端环境配置
```bash
cd backend
pip install -r requirements.txt
python app.py
```

## 环境要求

### 前端
- Node.js >= 14.0.0
- npm >= 6.14.0

### 后端
- Python >= 3.8
- OpenAI API Key（需要在.env文件中配置）

## 使用说明

1. 启动系统
   - 启动后端服务：`python app.py`
   - 启动前端服务：`npm start`

2. 简历智能问答流程
   - 上传简历开始问答
   - 依次完成三个部分的问答：
     - 项目经验（4个主问题，每个2个子问题）
     - 个人优势（3个主问题，每个2个子问题）
     - 编程能力（4个独立编程题）
   - 系统自动评估并生成报告

3. 注意事项
   - 总时间限制为2小时
   - 每部分必须完成所有问题才能进入下一部分
   - 最后5分钟会有时间提醒
   - 时间到自动提交

## 配置说明

### 前端配置
在 `.env` 文件中配置：
```
REACT_APP_API_URL=http://localhost:8000
```

### 后端配置
在 `.env` 文件中配置：
```
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=your_api_base_url
```

## 开发说明

### 目录结构
```
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Interview.tsx
│   │   │   └── Results.tsx
│   │   └── components/
├── backend/
│   ├── app.py
│   ├── services/
│   │    ├── interview_generator.py
│   │    └── answer_assessor.py
│   ├── parser/
|   ├── qa_enging/


```

## 技术栈

### 前端
- React
- TypeScript
- Material-UI
- Axios

### 后端
- Python
- Flask
- OpenAI API
- dotenv 

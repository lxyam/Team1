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
├─backend/ 后端代码
│  ├─__init__.py
│  ├─pipeline.py                 # 核心流程处理
│  ├─report.py                   # 报告生成模块
│  ├─code/
│  │  └─code_recommender.py      # 编程能力评估模块
│  ├─parser/
│  │  ├─__init__.py
│  │  └─extractor.py             # 简历解析器
│  ├─qa_engine/                  # 问答引擎
│  │  ├─__init__.py
│  │  ├─advantages.py            # 个人优势评估
│  │  ├─item.py                  # 项目经验评估
│  │  └─item_enhanced.py         # 增强项目评估
│  └─test/                       # 测试目录
│      ├─__init__.py
│      ├─app.py                  # 测试应用
│      ├─test_extractor.py       # 解析器测试
│      └─test_qa.py              # 问答测试
│
├─demo/                          # 演示示例
│  ├─README.md
│  ├─backend/
│  │  ├─app.py                   # 示例后端应用
│  │  ├─requirements.txt         # 依赖配置
│  │  └─services/                # 服务模块
│  └─frontend/                   # 示例前端
│      ├─package.json            # 项目配置
│      ├─public/                 # 静态资源
│      ├─src/                    # 源代码
│      └─tsconfig.json           # TypeScript配置
│
├─frontend/                      # 主项目前端
│  └─frontend.py                 # 前端入口
│
├─.gitignore                     # Git忽略配置
├─LICENSE                        # 许可证
├─README.md                      # 项目说明
└─requirements.txt               # Python依赖
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

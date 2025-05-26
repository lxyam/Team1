from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
from backend.pipeline import extract_resume, projects_main, advantages_main, generate_interview_code_question, evaluation, client

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnswerData(BaseModel):
    questionId: str
    answer: str
    isFollowUp: bool = False
    parentQuestionId: str = None

@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        print(f"接收到文件上传请求: {file.filename}, 大小: {file.size}")
        
        # 检查文件类型
        if not file.filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
            return {"error": "不支持的文件类型，请上传 PDF、DOC、DOCX 或 TXT 文件"}
        
        # 读取文件内容
        content = await file.read()
        print(f"文件内容读取完成，大小: {len(content)} 字节")
        
        # 保存上传的文件
        import os
        os.makedirs("backend/test/data", exist_ok=True)
        file_path = f"backend/test/data/{file.filename}"
        
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        print(f"文件保存成功: {file_path}")
        
        # 解析简历
        print("开始解析简历...")
        resume = extract_resume(file_path)
        if not resume:
            return {"error": "简历解析失败"}
        print("简历解析完成")
        
        # 生成面试问题
        print("开始生成面试问题...")
        projects_dict = projects_main(resume, client)
        # 转成数组
        projects = []
        for project_name, qa_list in projects_dict.items():
            for qa in qa_list:
                projects.append({
                    "projectName": project_name,
                    "question": qa.get("question"),
                    "answer": qa.get("answer")
                })
        
        advantages = advantages_main(resume, client)
        code = generate_interview_code_question(resume, client)
        print("面试问题生成完成")
        
        return {
            "resume": resume,
            "questions": {
                "projects": projects,
                "advantages": advantages,
                "code": code
            }
        }
    except Exception as e:
        print(f"处理文件上传时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/api/interview/evaluate")
async def evaluate_interview(answers: List[AnswerData]):
    try:
        # 将答案转换为后端需要的格式
        project_qa = {}
        advantages = {}
        code = None
        
        for answer in answers:
            if answer.questionId.startswith("project_"):
                # 提取项目名称（假设格式为 project_0, project_1 等）
                project_index = answer.questionId.split("_")[1]
                project_name = f"项目{project_index}"
                if project_name not in project_qa:
                    project_qa[project_name] = []
                project_qa[project_name].append({
                    "question": answer.questionId,
                    "answer": answer.answer
                })
            elif answer.questionId.startswith("advantage_"):
                advantages = {
                    "question": answer.questionId,
                    "answer": answer.answer
                }
            elif answer.questionId.startswith("code_"):
                code = (answer.questionId, answer.answer)
        
        # 生成评估报告
        report = evaluation(client, project_qa, advantages, code, {})
        return report
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 
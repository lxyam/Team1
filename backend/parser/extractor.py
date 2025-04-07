import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class ResumeExtractor:
    def __init__(self):
        OPENAI_API_KEY="sk-06a1fc23f04940cf93e06e4b39e1f949"
        OPENAI_API_BASE="https://api.deepseek.com"
        OPENAI_MODEL = "deepseek-chat"

        self.api_key = OPENAI_API_KEY
        self.api_base = OPENAI_API_BASE
        self.model = OPENAI_MODEL

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )

    def extract(self, resume_text: str) -> dict:
        system_prompt = """你是一个专业的简历解析助手。请分析简历内容，提取以下信息并直接返回JSON格式数据（不要添加任何markdown标记）：
        {
            "education": [
                {
                    "school": "学校名称",
                    "degree": "学位",
                    "major": "专业",
                    "graduation_year": "毕业年份"
                }
            ],
            "projects": [
                {
                    "name": "项目名称",
                    "description": "项目描述",
                    "technologies": ["使用的技术"],
                    "responsibilities": ["职责"],
                    "achievements": ["成就"]
                }
            ],
            "work_experience": [
                {
                    "company": "公司名称",
                    "position": "职位",
                    "duration": "工作时间",
                    "responsibilities": ["职责"],
                    "achievements": ["成就"]
                }
            ],
            "skills": ["技能列表"],
            "advantages": ["个人优势"]
        }

        注意：
        1. 直接返回JSON数据，不要添加任何markdown标记
        2. 如果某些信息在简历中没有提到，对应的字段返回空列表
        3. 确保所有字段都存在，即使是空值"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": resume_text}
                ],
                stream=False
            )

            content = response.choices[0].message.content.strip()

            if content.startswith("```"):
                content = content.split('\n', 1)[1].rsplit('\n', 1)[0]
            if content.startswith('json'):
                content = content.split('\n', 1)[1]

            data = json.loads(content)
            for key in ["education", "projects", "work_experience", "skills", "advantages"]:
                if key not in data:
                    data[key] = []

            return data

        except Exception as e:
            print(f"[❌] 提取失败: {e}")
            return {
                "education": [],
                "projects": [],
                "work_experience": [],
                "skills": [],
                "advantages": []
            }
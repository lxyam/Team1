import json
from dotenv import load_dotenv
from openai import OpenAI
import chardet
from docx import Document
import pdfplumber
import os
import io

load_dotenv()

OPENAI_API_KEY = "sk-06a1fc23f04940cf93e06e4b39e1f949"
OPENAI_API_BASE = "https://api.deepseek.com"
OPENAI_MODEL = "deepseek-chat"

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE
)

def read_file_smart(file_source) -> str:
    ext = None

    if isinstance(file_source, str):
        ext = os.path.splitext(file_source)[1].lower()
        file_obj = open(file_source, 'rb')
    else:
        filename = getattr(file_source, 'filename', '')
        ext = os.path.splitext(filename)[1].lower()
        file_obj = file_source

    if ext == '.docx':
        file_content = file_obj.read()
        docx_obj = io.BytesIO(file_content)
        doc = Document(docx_obj)
        return '\n'.join([para.text for para in doc.paragraphs])

    elif ext == '.pdf':
        file_content = file_obj.read()
        pdf_obj = io.BytesIO(file_content)
        text = ""
        with pdfplumber.open(pdf_obj) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    else:
        raw = file_obj.read()
        result = chardet.detect(raw)
        encoding = result['encoding']
        return raw.decode(encoding)

def extract_resume(file_source) -> dict:
    """
    提取简历关键信息的接口。

    输入：
        file_source: 支持两种类型
            - str，本地文件路径，例如 '/path/to/resume.docx'
            - file-like对象，例如 Flask中 request.files['file'] 上传的文件对象

    输出：
        dict，包含以下JSON结构：
        {
            "education": [...],
            "projects": [...],
            "work_experience": [...],
            "skills": [...],
            "advantages": [...]
        }
    如果提取失败，将返回空字典 {}。
    """
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
        resume_text = read_file_smart(file_source)

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
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

        issues = check_resume_issues(data)
        if issues:
            raise ValueError(f"简历信息不足，存在以下问题：{'; '.join(issues)}")

        return data

    except Exception as e:
        print(f"[❌] 提取失败: {e}")
        return {}

def check_resume_issues(data: dict) -> list:
    issues = []

    if not data["projects"]:
        issues.append("缺少项目经历")
    else:
        for p in data["projects"]:
            if not p["technologies"]:
                issues.append(f"项目《{p['name']}》缺少技术栈")
            if not p["achievements"]:
                issues.append(f"项目《{p['name']}》缺少成果描述")
            if not p["description"]:
                issues.append(f"项目《{p['name']}》缺少项目描述")


    if not data["advantages"]:
        issues.append("缺少个人优势")
    if not data["skills"]:
        issues.append("缺少技能列表")

    return issues
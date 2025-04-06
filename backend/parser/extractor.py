import io
import json
import logging
import docx
import PyPDF2
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

class ResumeExtractor:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE")
        self.model = os.getenv("OPENAI_MODEL", "deepseek-chat")

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
        
app = Flask(__name__)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def extract_text_from_pdf(pdf_file):
    try:
        logger.info("Starting PDF text extraction")
        file_content = pdf_file.read()
        pdf_file_obj = io.BytesIO(file_content)

        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")
            return text
        finally:
            pdf_file_obj.close()
    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}", exc_info=True)
        raise

def extract_text_from_docx(docx_file):
    try:
        logger.info("Starting DOCX text extraction")
        file_content = docx_file.read()
        docx_file_obj = io.BytesIO(file_content)

        try:
            doc = docx.Document(docx_file_obj)
            text = "\n".join([p.text for p in doc.paragraphs])
            if not text.strip():
                raise ValueError("No text could be extracted from the DOCX file")
            return text
        finally:
            docx_file_obj.close()
    except Exception as e:
        logger.error(f"DOCX extraction error: {str(e)}", exc_info=True)
        raise

@app.route('/api/interviews/upload', methods=['POST', 'OPTIONS'])
def upload_resume():
    if request.method == 'OPTIONS':
        return '', 204  # 处理预检请求

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = file.filename.lower()

    try:
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        extractor = ResumeExtractor()
        extracted_data = extractor.extract(text)
        return jsonify(extracted_data), 200

    except Exception as e:
        logger.error(f"Resume processing failed: {str(e)}", exc_info=True)
        return jsonify({"error": "Resume processing failed", "details": str(e)}), 500
    
#
# if __name__ == "__main__":
#    app.run(host="127.0.0.1", port=5088, debug=True)
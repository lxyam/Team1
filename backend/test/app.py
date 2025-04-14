import io
import json
import logging
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import docx
import PyPDF2
from flask import Flask, request, jsonify
from flask_cors import CORS
from qa_engine.interview_api_flask import flask_router as interview_flask_router

app = Flask(__name__)
CORS(app)  # 启用跨域支持
logger = logging.getLogger(__name__)

# 调整日志级别为WARNING，减少输出
logging.basicConfig(level=logging.WARNING)

# 设置werkzeug日志级别为WARNING
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# 注册面试API路由
app.register_blueprint(interview_flask_router, url_prefix='/interview')

# 添加一个直接的测试路由，不通过蓝图
@app.route('/test', methods=['GET'])
def direct_test():
    """直接测试Flask应用是否正常工作"""
    return jsonify({"message": "Flask应用正常工作", "status": "success"}), 200

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

    # 检查请求中是否有文件
    if 'file' not in request.files and 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    # 兼容两种参数名：'file'和'resume'
    file = request.files.get('file') or request.files.get('resume')
    filename = file.filename.lower()

    try:
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        # 导入ResumeExtractor
        from backend.parser.extractor import ResumeExtractor
        
        extractor = ResumeExtractor()
        extracted_data = extractor.extract(text)
        return jsonify(extracted_data), 200

    except Exception as e:
        logger.error(f"Resume processing failed: {str(e)}", exc_info=True)
        return jsonify({"error": "Resume processing failed", "details": str(e)}), 500

@app.route('/api/interviews/generate_questions', methods=['POST', 'OPTIONS'])
def generate_questions():
    if request.method == 'OPTIONS':
        return '', 204  # 处理预检请求

    try:
        # 获取请求数据
        data = request.json
        if not data or 'project' not in data or 'question_types' not in data:
            return jsonify({"error": "Missing required fields: project and question_types"}), 400

        # 导入ProjectQAGenerator
        from backend.qa_engine.item import ProjectQAGenerator

        # 创建问答生成器实例
        qa_generator = ProjectQAGenerator()

        # 生成问答数据
        qa_data = qa_generator.generate_questions(
            project_data=data['project'],
            question_types=data['question_types']
        )

        return jsonify(qa_data), 200

    except Exception as e:
        logger.error(f"Question generation failed: {str(e)}", exc_info=True)
        return jsonify({"error": "Question generation failed", "details": str(e)}), 500


if __name__ == "__main__":
    print("Starting AI Interview Backend Server on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
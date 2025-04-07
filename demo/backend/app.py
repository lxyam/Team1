import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import docx
import logging
import io
from services.resume_parser import ResumeParser
from services.interview_generator import InterviewGenerator
from services.answer_assessor import AnswerAssessor

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 配置CORS，允许所有来源
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],  # 明确指定允许的源
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "expose_headers": ["Content-Type", "Content-Length"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

@app.before_request
def log_request_info():
    """记录请求信息"""
    logger.debug('Headers: %s', dict(request.headers))
    logger.debug('Method: %s', request.method)
    logger.debug('URL: %s', request.url)
    if request.files:
        logger.debug('Files: %s', list(request.files.keys()))
        for key in request.files:
            file = request.files[key]
            logger.debug('File %s: filename=%s, content_type=%s', 
                        key, file.filename, file.content_type)

@app.after_request
def after_request(response):
    """记录响应信息"""
    logger.debug('Response status: %s', response.status)
    logger.debug('Response headers: %s', dict(response.headers))
    return response


# 存储面试数据
interviews = {}

def extract_text_from_pdf(pdf_file):
    """从PDF文件中提取文本"""
    try:
        logger.info("Starting PDF text extraction")
        # 保存文件内容到内存中
        file_content = pdf_file.read()
        logger.debug(f"Read {len(file_content)} bytes from file")
        
        # 创建内存文件对象
        pdf_file_obj = io.BytesIO(file_content)
        
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
            text = ""
            
            # 记录PDF页数
            num_pages = len(pdf_reader.pages)
            logger.debug(f"PDF has {num_pages} pages")
            
            for page_num in range(num_pages):
                logger.debug(f"Processing page {page_num + 1}")
                page = pdf_reader.pages[page_num]
                try:
                    page_text = page.extract_text()
                    logger.debug(f"Page {page_num + 1} text length: {len(page_text)}")
                    text += page_text
                except Exception as e:
                    logger.error(f"Error extracting text from page {page_num + 1}: {str(e)}")
                    continue
            
            # 检查提取的文本
            if not text.strip():
                logger.error("Extracted text is empty")
                raise ValueError("No text could be extracted from the PDF")
                
            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            logger.debug(f"First 200 characters of extracted text: {text[:200]}")
            
            return text
        finally:
            pdf_file_obj.close()
            
    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}", exc_info=True)
        raise

def extract_text_from_docx(docx_file):
    """从DOCX文件中提取文本"""
    try:
        logger.info("Starting DOCX text extraction")
        # 保存文件内容到内存中
        file_content = docx_file.read()
        logger.debug(f"Read {len(file_content)} bytes from file")
        
        # 创建内存文件对象
        docx_file_obj = io.BytesIO(file_content)
        
        try:
            doc = docx.Document(docx_file_obj)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            if not text.strip():
                logger.error("Extracted text is empty")
                raise ValueError("No text could be extracted from the DOCX file")
                
            logger.info(f"Successfully extracted {len(text)} characters from DOCX")
            logger.debug(f"First 200 characters of extracted text: {text[:200]}")
            
            return text
        finally:
            docx_file_obj.close()
            
    except Exception as e:
        logger.error(f"DOCX extraction error: {str(e)}", exc_info=True)
        raise

@app.route('/api/interviews/upload', methods=['POST', 'OPTIONS'])
def upload_resume():
    """处理简历上传"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        logger.info("Received resume upload request")
        logger.debug(f"Request method: {request.method}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        logger.debug(f"Request files: {request.files}")
        
        if 'resume' not in request.files:
            logger.error("No resume file in request")
            return jsonify({'error': 'No resume file provided'}), 400
            
        file = request.files['resume']
        if file.filename == '':
            logger.error("No selected file")
            return jsonify({'error': 'No file selected'}), 400
            
        # 获取文件扩展名
        file_ext = os.path.splitext(file.filename)[1].lower()
        logger.info(f"Processing file: {file.filename} with extension: {file_ext}")
        logger.debug(f"File content type: {file.content_type}")
        
        # 检查文件类型
        allowed_extensions = {'.pdf', '.doc', '.docx'}
        if file_ext not in allowed_extensions:
            logger.error(f"Unsupported file type: {file_ext}")
            return jsonify({'error': '仅支持 PDF 和 Word 文档格式'}), 400
        
        # 检查文件大小（10MB 限制）
        if len(file.read()) > 10 * 1024 * 1024:
            logger.error("File too large")
            return jsonify({'error': '文件大小不能超过 10MB'}), 400
        
        # 重置文件指针
        file.seek(0)
            
        # 根据文件类型提取文本
        try:
            if file_ext == '.pdf':
                text = extract_text_from_pdf(file)
            elif file_ext in ['.doc', '.docx']:
                text = extract_text_from_docx(file)
                
            # 创建ResumeParser实例并解析文本
            resume_parser = ResumeParser()
            resume_info = resume_parser.parse_resume(text)
            
            # 生成面试ID
            interview_id = str(uuid.uuid4())
            
            # 创建面试记录
            interview = {
                "id": interview_id,
                "resume": resume_info,
                "questions": [],
                "answers": [],
                "assessments": []
            }
            
            # 存储面试记录
            interviews[interview_id] = interview
            
            logger.info(f"Resume successfully processed, interview_id: {interview_id}")
            return jsonify({
                "status": "success",
                "message": "简历上传成功",
                "interview_id": interview_id
            })
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}", exc_info=True)
            return jsonify({
                'error': '文件处理失败，请确保文件内容正确且未损坏'
            }), 500
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        return jsonify({'error': '上传失败，请重试'}), 500

@app.route('/api/interviews/<interview_id>/questions', methods=['GET'])
def get_questions(interview_id):
    try:
        if interview_id not in interviews:
            return jsonify({"error": "Interview not found"}), 404
            
        interview = interviews[interview_id]
        
        # 获取查询参数
        question_type = request.args.get('type', 'project')
        count = int(request.args.get('count', 1))
        
        # 创建InterviewGenerator实例
        interview_generator = InterviewGenerator()
        
        # 生成指定数量和类型的问题
        questions = []
        for _ in range(count):
            question = interview_generator.generate_next_question(
                interview["resume"],
                interview["questions"],
                question_type
            )
            if question:
                questions.append(question)
                interview["questions"].append(question)
        
        return jsonify(questions)
            
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/interviews/<interview_id>/answers', methods=['POST'])
def submit_answer(interview_id):
    try:
        if interview_id not in interviews:
            return jsonify({"error": "Interview not found"}), 404
            
        data = request.get_json()
        if not data or "answer" not in data or "question_id" not in data:
            return jsonify({"error": "Invalid request data"}), 400
            
        interview = interviews[interview_id]
        
        # 查找对应的问题
        question = None
        for q in interview["questions"]:
            if q["id"] == data["question_id"]:
                question = q
                break
                
        if not question:
            return jsonify({"error": "Question not found"}), 404
            
        # 创建AnswerAssessor实例并评估答案
        answer_assessor = AnswerAssessor()
        assessment = answer_assessor.assess_answer(question, data["answer"])
        
        # 保存答案和评估结果
        answer_data = {
            "question_id": data["question_id"],
            "answer": data["answer"],
            "sub_question_index": data.get("sub_question_index"),  # 添加子问题索引
            "assessment": assessment
        }
        
        # 检查是否已存在该问题的答案
        existing_answer_index = None
        for i, ans in enumerate(interview["answers"]):
            if (ans["question_id"] == data["question_id"] and 
                ans.get("sub_question_index") == data.get("sub_question_index")):
                existing_answer_index = i
                break
        
        if existing_answer_index is not None:
            # 更新现有答案
            interview["answers"][existing_answer_index] = answer_data
        else:
            # 添加新答案
            interview["answers"].append(answer_data)
        
        return jsonify(assessment)
        
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/interviews/<interview_id>/report', methods=['GET'])
def get_interview_report(interview_id):
    """获取面试报告"""
    try:
        if interview_id not in interviews:
            logger.error(f"Interview {interview_id} not found")
            return jsonify({"error": "Interview not found"}), 404
            
        interview = interviews[interview_id]
        logger.info(f"Generating report for interview {interview_id}")
        logger.debug(f"Interview data: {interview}")
        
        # 生成报告
        report = {
            "resume": interview["resume"],
            "sections": {
                "project": [],
                "advantage": [],
                "coding": []
            },
            "overall_score": 0,
            "section_scores": {
                "project": 0,
                "advantage": 0,
                "coding": 0
            }
        }
        
        # 按部分组织问题和答案
        section_scores = {"project": [], "advantage": [], "coding": []}
        
        # 按类型组织问题
        questions_by_type = {"project": [], "advantage": [], "coding": []}
        for question in interview["questions"]:
            questions_by_type[question["type"]].append(question)
        
        # 处理每个部分的问题和答案
        for question_type in ["project", "advantage", "coding"]:
            type_questions = questions_by_type[question_type]
            
            for question in type_questions:
                question_data = {
                    "id": question["id"],
                    "question": question["question"],
                    "subQuestions": question.get("subQuestions", []),
                    "answers": []
                }
                
                # 查找该问题的所有答案
                question_answers = [
                    ans for ans in interview["answers"]
                    if ans["question_id"] == question["id"]
                ]
                
                if question.get("subQuestions"):
                    # 处理有子问题的情况
                    for i, _ in enumerate(question["subQuestions"]):
                        answer = next(
                            (ans for ans in question_answers 
                             if ans.get("sub_question_index") == i),
                            None
                        )
                        if answer:
                            answer_data = {
                                "answer": answer["answer"],
                                "score": answer["assessment"]["score"],
                                "feedback": answer["assessment"]["overall_comment"],
                                "sub_question_index": i
                            }
                            question_data["answers"].append(answer_data)
                            section_scores[question_type].append(answer["assessment"]["score"])
                else:
                    # 处理没有子问题的情况
                    if question_answers:
                        answer = question_answers[0]
                        answer_data = {
                            "answer": answer["answer"],
                            "score": answer["assessment"]["score"],
                            "feedback": answer["assessment"]["overall_comment"]
                        }
                        question_data["answers"].append(answer_data)
                        section_scores[question_type].append(answer["assessment"]["score"])
                
                report["sections"][question_type].append(question_data)
        
        # 计算每个部分的平均分
        for section in ["project", "advantage", "coding"]:
            scores = section_scores[section]
            if scores:
                report["section_scores"][section] = sum(scores) / len(scores)
        
        # 计算总分
        weights = {"project": 0.4, "advantage": 0.3, "coding": 0.3}
        weighted_scores = []
        
        for section, weight in weights.items():
            if section_scores[section]:
                section_avg = sum(section_scores[section]) / len(section_scores[section])
                weighted_scores.append(section_avg * weight)
        
        report["overall_score"] = sum(weighted_scores) if weighted_scores else 0
        
        logger.info(f"Successfully generated report for interview {interview_id}")
        logger.debug(f"Report data: {report}")
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 修改端口为8000以匹配前端请求
    logger.info("Starting server on port 8000...")
    app.run(debug=True, port=8000, host='0.0.0.0') 
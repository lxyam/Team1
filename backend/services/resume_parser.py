import os
import json
import openai
from dotenv import load_dotenv
import logging

# 配置日志
logger = logging.getLogger(__name__)

load_dotenv()

class ResumeParser:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        api_base = os.getenv('OPENAI_API_BASE')
        self.model = os.getenv('OPENAI_MODEL', 'deepseek-chat')
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        openai.api_key = api_key
        openai.api_base = api_base
        
    def parse_resume(self, resume_text):
        """解析简历内容"""
        try:
            logger.info("Starting resume parsing")
            logger.debug(f"Resume text length: {len(resume_text)}")
            logger.debug(f"Using model: {self.model}")
            logger.debug(f"API base: {openai.api_base}")
            
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": """你是一个专业的简历解析助手。请分析简历内容，提取以下信息并直接返回JSON格式数据（不要添加任何markdown标记）：
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
                        },
                        {
                            "role": "user",
                            "content": resume_text
                        }
                    ],
                    temperature=0.7,
                    request_timeout=60
                )
                logger.debug(f"API Response: {response}")
                
                # 解析返回的JSON字符串
                try:
                    content = response.choices[0].message.content.strip()
                    # 如果内容被markdown包裹，去除markdown标记
                    if content.startswith('```') and content.endswith('```'):
                        content = content.split('\n', 1)[1].rsplit('\n', 1)[0]
                    if content.startswith('```json'):
                        content = content.split('\n', 1)[1]
                    
                    logger.debug(f"Cleaned content: {content}")
                    resume_info = json.loads(content)
                    
                    # 确保所有必需的字段都存在
                    required_fields = ["education", "projects", "work_experience", "skills", "advantages"]
                    for field in required_fields:
                        if field not in resume_info:
                            resume_info[field] = []
                    
                    return resume_info
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {str(e)}")
                    logger.error(f"Failed content: {content}")
                    return {
                        "education": [],
                        "projects": [],
                        "work_experience": [],
                        "skills": [],
                        "advantages": []
                    }
                    
            except Exception as api_error:
                logger.error(f"API call error: {str(api_error)}", exc_info=True)
                raise
            
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}", exc_info=True)
            return {
                "education": [],
                "projects": [],
                "work_experience": [],
                "skills": [],
                "advantages": []
            } 
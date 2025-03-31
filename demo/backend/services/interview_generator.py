import os
import json
import uuid
import openai
from dotenv import load_dotenv
import logging

# 配置日志
logger = logging.getLogger(__name__)

load_dotenv()

class InterviewGenerator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        openai.api_key = api_key
        openai.api_base = api_base
        
    def generate_next_question(self, resume_info, previous_questions=None, question_type=None):
        """生成下一个面试问题"""
        try:
            if previous_questions is None:
                previous_questions = []

            # 构造系统提示，根据问题类型生成不同的提示
            system_prompts = {
                "project": """作为面试官，请根据候选人的项目经验生成有针对性的技术问题。要求：
                1. 生成一个主问题，并提供2个相关的子问题
                2. 每个子问题应该关注不同的技术点或项目方面
                3. 子问题应该由浅入深，循序渐进
                4. 避免重复之前已经问过的问题
                
                请按照以下格式返回：
                主问题：[主问题文本]
                
                子问题：
                1. [子问题1]
                2. [子问题2]""",
                
                "advantage": """作为面试官，请根据候选人的背景生成关于个人优势的问题。要求：
                1. 生成一个主问题，并提供2个相关的子问题
                2. 结合候选人的教育背景和技能特长
                3. 探讨个人成长和职业规划
                4. 避免重复之前已经问过的问题
                
                请按照以下格式返回：
                主问题：[主问题文本]
                
                子问题：
                1. [子问题1]
                2. [子问题2]""",
                
                "coding": """作为面试官，请根据候选人的技术栈生成一个高质量的编程问题。要求：
                1. 问题应该考察算法、数据结构或系统设计能力
                2. 结合候选人的技术背景设计难度合适的问题
                3. 问题要具体且有明确的要求
                4. 避免重复之前已经问过的问题
                
                请按照以下格式返回：
                问题：[详细的问题描述，包括具体要求和约束条件]"""
            }

            # 如果没有指定问题类型，则自动确定
            if question_type is None:
                question_type = self._determine_question_type(previous_questions)
            
            # 生成问题
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompts[question_type]
                    },
                    {
                        "role": "user",
                        "content": f"简历信息：{json.dumps(resume_info, ensure_ascii=False)}\n之前的问题：{json.dumps([q['question'] for q in previous_questions], ensure_ascii=False)}"
                    }
                ],
                temperature=0.8
            )
            
            # 解析返回的文本格式问题
            content = response.choices[0].message.content.strip()
            lines = content.split('\n')
            
            # 提取主问题
            main_question = ""
            for line in lines:
                if question_type == 'coding':
                    if line.startswith('问题：'):
                        main_question = line.replace('问题：', '').strip()
                        break
                else:
                    if line.startswith('主问题：'):
                        main_question = line.replace('主问题：', '').strip()
                        break
            
            # 提取子问题
            sub_questions = []
            if question_type != 'coding':  # 只有project和advantage类型需要子问题
                for line in lines:
                    if line.strip().startswith(('1.', '2.')):  # 限制只提取前两个子问题
                        sub_questions.append(line.split('.', 1)[1].strip())
            
            # 构造问题对象
            question = {
                "id": str(uuid.uuid4()),
                "type": question_type,
                "question": main_question,
                "subQuestions": sub_questions if question_type != 'coding' else None,
                "reference_answer": "",
                "difficulty": "hard" if question_type == "coding" else "medium",
                "points": 100 if question_type == "coding" else 80
            }
            
            return question
                
        except Exception as e:
            logger.error(f"Error generating question: {str(e)}", exc_info=True)
            return {
                "id": str(uuid.uuid4()),
                "type": question_type or "project",
                "question": "请描述一下您最近参与的一个项目。",
                "subQuestions": [
                    "您在项目中担任什么角色？",
                    "您是如何解决项目中的主要技术挑战的？"
                ],
                "reference_answer": "",
                "difficulty": "medium",
                "points": 80
            }

    def _determine_question_type(self, previous_questions):
        """确定下一个问题的类型"""
        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": """作为面试官，你需要确定下一个问题的类型。
                        可选的类型有：
                        1. project - 项目相关问题
                        2. advantage - 个人优势相关问题
                        3. coding - 编程相关问题
                        
                        请根据之前的问题，选择一个合适的类型。只需返回类型名称，不需要其他内容。"""
                    },
                    {
                        "role": "user",
                        "content": f"之前的问题：{previous_questions}"
                    }
                ],
                temperature=0.7
            )
            
            question_type = response.choices[0].message.content.strip().lower()
            return question_type if question_type in ["project", "advantage", "coding"] else "project"
            
        except Exception as e:
            logger.error(f"Error determining question type: {str(e)}", exc_info=True)
            return "project"

    def _generate_project_question(self, resume_info, previous_questions):
        """生成项目相关问题"""
        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": """作为面试官，你需要根据候选人的项目经验生成一个深入的技术问题。
                        问题应该：
                        1. 针对具体的项目细节
                        2. 考察技术深度
                        3. 关注问题解决能力
                        4. 避免重复之前的问题
                        
                        请直接返回问题，不需要其他内容。"""
                    },
                    {
                        "role": "user",
                        "content": f"简历信息：{resume_info}\n之前的问题：{previous_questions}"
                    }
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating project question: {str(e)}", exc_info=True)
            return "在您最具挑战性的项目中，您是如何解决技术难题的？"

    def _generate_advantage_question(self, resume_info, previous_questions):
        """生成个人优势相关问题"""
        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": """作为面试官，你需要生成一个关于候选人个人优势的问题。
                        问题应该：
                        1. 探索个人特质
                        2. 了解职业发展规划
                        3. 评估团队协作能力
                        4. 避免重复之前的问题
                        
                        请直接返回问题，不需要其他内容。"""
                    },
                    {
                        "role": "user",
                        "content": f"简历信息：{resume_info}\n之前的问题：{previous_questions}"
                    }
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating advantage question: {str(e)}", exc_info=True)
            return "您认为您最大的优势是什么？请举例说明。"

    def _generate_coding_question(self, resume_info, previous_questions):
        """生成编程相关问题"""
        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": """作为面试官，你需要生成一个编程相关的技术问题。
                        问题应该：
                        1. 考察核心编程概念
                        2. 结合候选人的技术栈
                        3. 包含实际场景应用
                        4. 避免重复之前的问题
                        
                        请直接返回问题，不需要其他内容。"""
                    },
                    {
                        "role": "user",
                        "content": f"简历信息：{resume_info}\n之前的问题：{previous_questions}"
                    }
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating coding question: {str(e)}", exc_info=True)
            return "请描述一个您熟悉的数据结构，并说明其适用场景。" 
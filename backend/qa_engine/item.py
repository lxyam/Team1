import os
import json
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import logging

# 设置openai相关模块日志级别为WARNING
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('openai._base_client').setLevel(logging.WARNING)

# 确保环境变量加载
load_dotenv()

class ProjectQAGenerator:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE")
        self.model = os.getenv("OPENAI_MODEL", "deepseek-chat")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )

    def generate_questions(self, project_data: Dict[str, Any], question_types: List[str]) -> List[Dict[str, Any]]:
        """根据项目信息和问题类型生成问答数据
        
        Args:
            project_data: 项目信息，包含name, description, technologies, responsibilities, achievements等字段
            question_types: 问题类型列表，可包含basic, technical, design, challenge等
            
        Returns:
            问答数据列表，每项包含question, answer, type, score_criteria字段
        """
        system_prompt = """
        你是一个专业的技术面试官。请根据候选人的项目经验，生成针对性的面试问题和参考答案。
        
        请根据提供的项目信息和指定的问题类型，生成相应的问答数据。每个问题应包含问题内容、参考答案、问题类型和评分标准。
        
        问题类型说明：
        - basic: 基础问题，验证项目基本情况和技术选型
        - technical: 技术问题，针对使用的核心技术提出深度问题
        - design: 设计问题，考察系统设计和架构能力
        - challenge: 挑战问题，探讨项目难点和解决方案
        
        返回的JSON格式如下：
        [
            {
                "question": "问题内容",
                "answer": "参考答案",
                "type": "问题类型(basic/technical/design/challenge)",
                "score_criteria": [
                    {"score": 1, "description": "评分标准描述1"},
                    {"score": 3, "description": "评分标准描述2"},
                    {"score": 5, "description": "评分标准描述3"}
                ]
            }
        ]
        
        注意：
        1. 直接返回JSON数据，不要添加任何markdown标记
        2. 每个问题类型至少生成1-2个问题
        3. 评分标准应包含3-5个等级，分数从低到高排列
        4. 问题和答案应该具体、专业，与项目技术相关
        """

        try:
            project_context = f"""
            项目名称：{project_data.get('name', '')}
            项目描述：{project_data.get('description', '')}
            使用技术：{', '.join(project_data.get('technologies', []))}
            项目职责：{', '.join(project_data.get('responsibilities', []))}
            项目成就：{', '.join(project_data.get('achievements', []))}
            问题类型：{', '.join(question_types)}
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": project_context}
                ],
                stream=False
            )

            content = response.choices[0].message.content.strip()
            if content.startswith('```'):
                content = content.split('\n', 1)[1].rsplit('\n', 1)[0]
            if content.startswith('json'):
                content = content.split('\n', 1)[1]

            qa_data = json.loads(content)
            return qa_data

        except Exception as e:
            print(f"[❌] 问题生成失败: {e}")
            return []

class InterviewSession:
    def __init__(self, project_data: Dict[str, Any]):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE")
        self.model = os.getenv("OPENAI_MODEL", "deepseek-chat")
        self.project_data = project_data
        self.conversation_history = []
        self.candidate_answers = []
        
        # 打印重要的调试信息
        print(f"初始化InterviewSession: API Key存在: {bool(self.api_key)}, API Base: {self.api_base}, Model: {self.model}")
        
        # 检查API密钥是否有效
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 环境变量未设置或为空")
            
        # 检查API基础URL是否有效
        if not self.api_base:
            print("警告: OPENAI_API_BASE 环境变量未设置，将使用默认URL")
            
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
                timeout=60.0  # 设置60秒超时
            )
            print("OpenAI客户端创建成功")
        except Exception as e:
            print(f"OpenAI客户端创建失败: {str(e)}")
            raise
            
    def _call_openai_with_retry(self, messages, max_retries=3):
        """调用OpenAI API，带有重试逻辑"""
        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=False
                )
                return response
            except Exception as e:
                last_error = e
                if attempt == 0:  # 仅在第一次尝试失败时打印消息
                    print(f"OpenAI API调用失败，正在重试... (错误: {str(e)[:50]})")
                if attempt < max_retries - 1:
                    time.sleep(2)  # 等待2秒后重试
        
        # 所有重试都失败
        if last_error:
            print(f"OpenAI API调用失败: {str(last_error)[:50]}")
            raise last_error
        return None

    def _get_interviewer_system_prompt(self) -> str:
        return """
        你是一个专业的技术面试官。请根据候选人的项目经验和回答，进行深入的面试对话。
        
        你的任务是：
        1. 根据项目信息提出有针对性的问题
        2. 根据候选人的回答进行追问或提出新的问题
        3. 如果候选人的回答不够深入或存在疑问，可以要求进一步解释
        4. 如果候选人的回答已经足够深入，可以转向新的问题方向
        
        请确保：
        1. 问题要具体、专业，与项目技术相关
        2. 追问要基于候选人的回答，不能偏离主题
        3. 保持对话的连贯性和逻辑性
        """

    def _get_candidate_system_prompt(self) -> str:
        return """
        你是一个经验丰富的技术候选人。请根据项目经验和面试官的问题，给出专业、深入的回答。注意：你的回答要是人与人之间的自然对话形式，不需要添加任何markdown标记。
        
        你的任务是：
        1. 提供详细的技术实现细节
        2. 展示对项目难点和解决方案的深入理解
        3. 体现良好的技术思维和表达能力
        
        请确保：
        1. 回答要具体、专业，包含实际的技术细节
        2. 展示对技术选型和架构设计的深入思考
        3. 突出个人在项目中的贡献和技术成长
        4. 保持回答的逻辑性和连贯性
        5. 通过自然对话的语言回答，不需要条条框框的
        """

    def start_interview(self) -> Dict[str, str]:
        """开始面试，生成第一个问题"""
        try:
            project_context = f"""
            项目名称：{self.project_data.get('name', '')}
            项目描述：{self.project_data.get('description', '')}
            使用技术：{', '.join(self.project_data.get('technologies', []))}
            项目职责：{', '.join(self.project_data.get('responsibilities', []))}
            项目成就：{', '.join(self.project_data.get('achievements', []))}
            """
            
            # print("正在生成第一个面试问题...")
            
            try:
                interviewer_messages = [
                    {"role": "system", "content": self._get_interviewer_system_prompt()},
                    {"role": "user", "content": f"请根据以下项目信息，提出第一个面试问题：\n{project_context}"}
                ]
                
                response = self._call_openai_with_retry(interviewer_messages)
                
                question = response.choices[0].message.content.strip()
                self.conversation_history.append({"role": "interviewer", "content": question})
                # print(question)
                # print("第一个问题生成成功，正在生成参考答案...")
                
                # 生成候选人的参考答案
                candidate_messages = [
                    {"role": "system", "content": self._get_candidate_system_prompt()},
                    {"role": "user", "content": f"请回答以下问题：\n{question}\n项目信息：\n{project_context}"}
                ]
                
                candidate_response = self._call_openai_with_retry(candidate_messages)
                
                candidate_answer = candidate_response.choices[0].message.content.strip()
                self.candidate_answers.append(candidate_answer)
                # print(candidate_answer)
                # print("参考答案生成成功")
                
                return {
                    "question": question,
                    "candidate_answer": candidate_answer
                }
            except Exception as e:
                print(f"OpenAI API调用失败: {str(e)}")
                # 返回一个默认问题和答案，避免整个流程中断
                default_question = "请详细介绍一下这个项目的技术架构和你负责的部分。"
                default_answer = "我负责的是简历解析模块和大模型对接部分。在技术架构上，我们使用了Python和FastAPI构建后端服务，PostgreSQL存储数据，并通过OpenAI API实现智能解析功能。"
                self.conversation_history.append({"role": "interviewer", "content": default_question})
                self.candidate_answers.append(default_answer)
                return {
                    "question": default_question,
                    "candidate_answer": default_answer
                }
        except Exception as e:
            print(f"start_interview方法异常: {str(e)}")
            raise

    def continue_interview(self, user_answer: str) -> Optional[Dict[str, str]]:
        """继续面试，根据用户回答生成下一个问题"""
        try:
            if len(self.conversation_history) >= 5:  # 最多5轮对话
                return None

            self.conversation_history.append({"role": "user", "content": user_answer})

            # 生成面试官的下一个问题
            conversation_context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in self.conversation_history
            ])
            
            # print("正在生成下一个面试问题...")
            
            try:
                interviewer_messages = [
                    {"role": "system", "content": self._get_interviewer_system_prompt()},
                    {"role": "user", "content": f"请根据以下对话历史，提出下一个问题：\n{conversation_context}"}
                ]
                
                response = self._call_openai_with_retry(interviewer_messages)
                
                question = response.choices[0].message.content.strip()
                self.conversation_history.append({"role": "interviewer", "content": question})
                
                # print("问题生成成功，正在生成参考答案...")
                
                # 生成候选人的参考答案
                candidate_messages = [
                    {"role": "system", "content": self._get_candidate_system_prompt()},
                    {"role": "user", "content": f"请回答以下问题：\n{question}\n项目信息：\n{self._get_project_context()}"}
                ]
                
                candidate_response = self._call_openai_with_retry(candidate_messages)
                
                candidate_answer = candidate_response.choices[0].message.content.strip()
                self.candidate_answers.append(candidate_answer)
                
                # print("参考答案生成成功")
                
                return {
                    "question": question,
                    "candidate_answer": candidate_answer
                }
            except Exception as e:
                print(f"OpenAI API调用失败: {str(e)}")
                # 返回一个默认问题和答案，避免整个流程中断
                default_question = "您能更详细地介绍一下项目中遇到的技术挑战和解决方案吗？"
                default_answer = "在项目中我们面临的主要挑战是文档格式多样性和非结构化文本解析。对于格式多样性，我们使用了python-docx和PyPDF2库处理不同格式；对于文本解析，结合了规则和大模型方法，提高了准确率。"
                self.conversation_history.append({"role": "interviewer", "content": default_question})
                self.candidate_answers.append(default_answer)
                return {
                    "question": default_question,
                    "candidate_answer": default_answer
                }
        except Exception as e:
            print(f"continue_interview方法异常: {str(e)}")
            raise

    def evaluate_answers(self) -> Dict[str, Any]:
        """评估用户回答"""
        try:
            user_answers = [msg["content"] for msg in self.conversation_history if msg["role"] == "user"]
            
            evaluation_prompt = f"""
            请评估候选人的回答质量。以下是对话历史：

            项目信息：
            {self._get_project_context()}

            对话历史：
            {self._format_conversation_history()}

            参考答案：
            {self._format_candidate_answers()}

            请从以下几个方面进行评估：
            1. 技术深度：对技术细节的理解和掌握程度
            2. 表达能力：回答的清晰度和逻辑性
            3. 项目理解：对项目整体架构和关键点的把握
            4. 问题解决：展示的问题分析和解决能力

            请给出具体的评分（1-5分）和评价。
            """
            
            # print("正在生成面试评估结果...")
            
            try:
                evaluation_messages = [
                    {"role": "system", "content": "你是一个专业的面试评估专家。"},
                    {"role": "user", "content": evaluation_prompt}
                ]
                
                response = self._call_openai_with_retry(evaluation_messages)
                
                evaluation = response.choices[0].message.content.strip()
                # print("评估结果生成成功")
                
                return {
                    "evaluation": evaluation,
                    "conversation_history": self.conversation_history,
                    "candidate_answers": self.candidate_answers
                }
            except Exception as e:
                print(f"OpenAI API调用失败: {str(e)}")
                # 返回默认评估结果
                default_evaluation = """
                ## 技术面试评估报告

                ### 技术深度: 3/5
                候选人展示了对项目的基本技术理解，但缺乏深入细节。

                ### 表达能力: 4/5
                回答表达清晰，逻辑结构良好。

                ### 项目理解: 3/5
                对项目有基本理解，但对整体架构的描述不够全面。

                ### 问题解决: 3/5
                能够描述基本的解决方案，但缺乏对技术挑战的深入分析。

                ### 总体评价
                候选人具备基本的技术能力和项目经验，建议进行下一轮技术测试以进一步评估。
                """
                return {
                    "evaluation": default_evaluation,
                    "conversation_history": self.conversation_history,
                    "candidate_answers": self.candidate_answers
                }
        except Exception as e:
            print(f"evaluate_answers方法异常: {str(e)}")
            raise

    def _get_project_context(self) -> str:
        return f"""
        项目名称：{self.project_data.get('name', '')}
        项目描述：{self.project_data.get('description', '')}
        使用技术：{', '.join(self.project_data.get('technologies', []))}
        项目职责：{', '.join(self.project_data.get('responsibilities', []))}
        项目成就：{', '.join(self.project_data.get('achievements', []))}
        """

    def _format_conversation_history(self) -> str:
        return "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in self.conversation_history
        ])

    def _format_candidate_answers(self) -> str:
        return "\n\n".join([
            f"问题 {i+1} 的参考答案：\n{answer}"
            for i, answer in enumerate(self.candidate_answers)
        ])
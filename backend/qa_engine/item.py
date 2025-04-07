import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

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

    def generate_project_questions(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据项目经验生成多层次问答"""
        system_prompt = """
        你是一个专业的技术面试官。请根据候选人的项目经验，生成一系列由浅入深的技术问题。问题应该包含以下层次：
        1. 基础理解：验证项目基本情况和技术选型
        2. 技术深度：针对使用的核心技术提出深度问题
        3. 方案设计：考察系统设计和架构能力
        4. 优化改进：探讨性能优化和可扩展性
        5. 反思总结：项目难点和解决方案

        返回的JSON格式如下：
        {
            "questions": [
                {
                    "level": "基础理解/技术深度/方案设计/优化改进/反思总结",
                    "question": "问题内容",
                    "expected_answer": "参考答案要点",
                    "evaluation_criteria": ["评分要点1", "评分要点2"]
                }
            ]
        }
        """

        try:
            project_context = f"""
            项目名称：{project_data.get('name', '')}
            项目描述：{project_data.get('description', '')}
            使用技术：{', '.join(project_data.get('technologies', []))}
            项目职责：{', '.join(project_data.get('responsibilities', []))}
            项目成就：{', '.join(project_data.get('achievements', []))}
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
            return qa_data.get('questions', [])

        except Exception as e:
            print(f"[❌] 问题生成失败: {e}")
            return []

    def generate_skill_questions(self, skills: List[str]) -> List[Dict[str, Any]]:
        """根据技能清单生成技术问题"""
        system_prompt = """
        你是一个专业的技术面试官。请根据候选人的技能清单，生成针对性的技术问题。问题应该：
        1. 覆盖各个技术领域
        2. 包含理论知识和实践应用
        3. 设置不同难度等级

        返回的JSON格式如下：
        {
            "questions": [
                {
                    "skill": "具体技能",
                    "level": "基础/进阶/专家",
                    "question": "问题内容",
                    "expected_answer": "参考答案要点",
                    "evaluation_criteria": ["评分要点1", "评分要点2"]
                }
            ]
        }
        """

        try:
            skills_context = f"技能清单：{', '.join(skills)}"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": skills_context}
                ],
                stream=False
            )

            content = response.choices[0].message.content.strip()
            if content.startswith('```'):
                content = content.split('\n', 1)[1].rsplit('\n', 1)[0]
            if content.startswith('json'):
                content = content.split('\n', 1)[1]

            qa_data = json.loads(content)
            return qa_data.get('questions', [])

        except Exception as e:
            print(f"[❌] 问题生成失败: {e}")
            return []
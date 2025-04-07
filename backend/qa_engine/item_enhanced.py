import os
import json
from typing import List, Dict, Any, Optional
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

    def _get_project_type(self, technologies: List[str]) -> str:
        """根据技术栈判断项目类型"""
        ai_ml_keywords = {"tensorflow", "pytorch", "scikit-learn", "机器学习", "深度学习", "nlp", "计算机视觉"}
        web_keywords = {"react", "vue", "angular", "node", "django", "flask", "spring", "前端", "后端"}
        
        tech_set = set(t.lower() for t in technologies)
        if any(k in tech_set for k in ai_ml_keywords):
            return "ai_ml"
        elif any(k in tech_set for k in web_keywords):
            return "web_development"
        return "web_development"  # 默认web开发

    def _generate_candidate_answers(self, project_data: Dict[str, Any], questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """让候选人LLM根据项目背景生成标准答案模板"""
        candidate_prompt = """
        你是一位经验丰富的技术人员，正在参加技术面试。请根据你的项目背景，对面试官的问题进行专业、全面的回答。
        
        回答要求：
        1. 结构清晰，逻辑严密
        2. 结合项目实际经验
        3. 突出技术深度和广度
        4. 展示问题解决能力
        5. 适当强调个人贡献
        
        请确保你的回答：
        - 准确回应问题要点
        - 提供具体的技术细节和实践案例
        - 展示系统性思维和技术决策能力
        - 表达专业且容易理解
        """
        
        try:
            for question in questions:
                # 构建问答上下文
                qa_context = {
                    "project_background": project_data,
                    "main_question": question["main_question"],
                    "follow_up_questions": question["follow_up_questions"]
                }
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": candidate_prompt},
                        {"role": "user", "content": json.dumps(qa_context, ensure_ascii=False)}
                    ],
                    stream=False
                )
                
                content = response.choices[0].message.content.strip()
                answers = json.loads(content)
                question["answers"] = answers
            
            return questions
        except Exception as e:
            print(f"[❌] 生成候选人答案失败: {e}")
            return questions

    def generate_questions(self, project_data: Dict[str, Any], question_types: List[str]) -> List[Dict[str, Any]]:
        """根据项目信息和问题类型生成问答数据"""
        system_prompt = """
        你是一个专业的技术面试官。请根据候选人的项目经验，生成针对性的面试问题和参考答案。
        
        你需要深入分析项目信息，从以下维度思考并提出问题：
        1. 技术挑战和解决方案
        2. 性能优化和工程实践
        3. 团队协作和项目管理
        4. 需求变更和应对策略
        5. 架构设计和技术选型
        6. 项目中的关键技术细节
        
        针对项目中使用的每项核心技术，深入提问：
        1. 技术选型的原因和对比
        2. 实现过程中的难点和解决方案
        3. 性能优化和最佳实践
        4. 踩坑经历和经验总结
        
        每个问题应包含：
        1. 主问题
        2. 2-3个相关的追问
        3. 参考答案
        4. 评分维度（技术理解、实践经验、解决方案、表达能力）
        
        问题类型说明：
        - basic: 基础问题，验证项目基本情况和技术选型
        - technical: 技术问题，针对使用的核心技术提出深度问题
        - design: 设计问题，考察系统设计和架构能力
        - challenge: 挑战问题，探讨项目难点和解决方案
        
        返回的JSON格式如下：
        [
            {
                "main_question": "主问题内容",
                "follow_up_questions": [
                    "追问1",
                    "追问2"
                ],
                "answers": {
                    "main": "主问题参考答案",
                    "follow_up": [
                        "追问1参考答案",
                        "追问2参考答案"
                    ]
                },
                "type": "问题类型",
                "scoring_dimensions": {
                    "technical_understanding": {
                        "weight": 0.3,
                        "criteria": [
                            {"score": 1, "description": "基础评分标准"},
                            {"score": 3, "description": "中等评分标准"},
                            {"score": 5, "description": "优秀评分标准"}
                        ]
                    },
                    "practical_experience": {
                        "weight": 0.3,
                        "criteria": [...]
                    },
                    "solution_quality": {
                        "weight": 0.2,
                        "criteria": [...]
                    },
                    "communication": {
                        "weight": 0.2,
                        "criteria": [...]
                    }
                }
            }
        ]
        """

        try:
            # 构建项目上下文
            project_context = f"""
            项目名称：{project_data.get('name', '')}
            项目描述：{project_data.get('description', '')}
            使用技术：{', '.join(project_data.get('technologies', []))}
            项目职责：{', '.join(project_data.get('responsibilities', []))}
            项目成就：{', '.join(project_data.get('achievements', []))}
            问题类型：{', '.join(question_types)}
            """

            # 1. 面试官LLM生成问题
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

            questions = json.loads(content)
            
            # 2. 候选人LLM生成标准答案
            questions = self._generate_candidate_answers(project_data, questions)

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

    def evaluate_answer(self, question_data: Dict[str, Any], answer: str, is_follow_up: bool = False) -> Dict[str, Any]:
        """评估候选人的回答
        
        Args:
            question_data: 问题数据，包含问题内容和评分标准
            answer: 候选人的回答
            is_follow_up: 是否是追问的回答
            
        Returns:
            评估结果，包含各维度得分和总分
        """
        system_prompt = """
        你是一个专业的技术面试评估专家。请根据标准答案模板和候选人的实际回答进行对比评估。
        
        评估要求：
        1. 对比标准答案和实际回答的差异
        2. 根据评分维度进行客观打分
        3. 提供具体的改进建议
        
        评估维度包括：
        1. 技术理解（对相关技术的理解深度和广度）
        2. 实践经验（实际项目经验和问题解决能力）
        3. 解决方案（方案的完整性、合理性和创新性）
        4. 表达能力（语言组织、逻辑清晰度）
        
        请返回JSON格式的评估结果：
        {
            "dimensions": {
                "technical_understanding": {
                    "score": 分数,
                    "comments": "评价意见",
                    "gap_analysis": "与标准答案的差距",
                    "improvement": "改进建议"
                },
                ...
            },
            "total_score": 总分,
            "feedback": "总体评价",
            "key_differences": ["与标准答案的主要差异点"],
            "strengths": ["回答的优点"],
            "weaknesses": ["需要改进的地方"]
        }
        """

        try:
            eval_context = {
                "question": question_data["main_question" if not is_follow_up else "follow_up_questions"],
                "answer": answer,
                "scoring_dimensions": question_data["scoring_dimensions"],
                "is_follow_up": is_follow_up
            }

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(eval_context, ensure_ascii=False)}
                ],
                stream=False
            )

            content = response.choices[0].message.content.strip()
            if content.startswith('```'):
                content = content.split('\n', 1)[1].rsplit('\n', 1)[0]
            if content.startswith('json'):
                content = content.split('\n', 1)[1]

            eval_result = json.loads(content)
            return eval_result

        except Exception as e:
            print(f"[❌] 答案评估失败: {e}")
            return {
                "dimensions": {},
                "total_score": 0,
                "feedback": "评估失败"
            }
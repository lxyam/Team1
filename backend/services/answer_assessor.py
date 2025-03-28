import os
import json
import openai
from dotenv import load_dotenv
import logging

# 配置日志
logger = logging.getLogger(__name__)

load_dotenv()

class AnswerAssessor:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        openai.api_key = api_key
        openai.api_base = api_base
        
    def assess_answer(self, question, answer):
        """评估面试答案"""
        try:
            # 如果答案为空或只包含空白字符，直接返回0分
            if not answer or not answer.strip():
                return {
                    "score": 0,
                    "accuracy": "未作答",
                    "completeness": "未作答",
                    "technical_depth": "未作答",
                    "clarity": "未作答",
                    "suggestions": "请认真作答",
                    "overall_comment": "未作答"
                }

            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": """作为面试评估专家，你需要对候选人的回答进行严格评估。
                        评估维度包括：
                        1. 准确性（30分）- 回答是否准确，是否有错误
                        2. 完整性（25分）- 是否完整回答了问题的各个方面
                        3. 技术深度（25分）- 是否展示了足够的技术理解深度
                        4. 表达清晰度（20分）- 回答是否清晰、逻辑连贯
                        
                        总分计算规则：
                        1. 如果答案少于50字，最高分不超过30分
                        2. 如果答案包含明显错误，最高分不超过50分
                        3. 如果答案泛泛而谈，没有具体细节，最高分不超过60分
                        4. 优秀答案（90分以上）必须包含具体的技术细节和实践经验
                        
                        请以JSON格式返回评估结果：
                        {
                            "score": 分数（0-100）,
                            "accuracy": "准确性评价",
                            "completeness": "完整性评价",
                            "technical_depth": "技术深度评价",
                            "clarity": "表达清晰度评价",
                            "suggestions": "改进建议",
                            "overall_comment": "总体评价"
                        }"""
                    },
                    {
                        "role": "user",
                        "content": f"问题：{question}\n\n回答：{answer}"
                    }
                ],
                temperature=0.7
            )
            
            try:
                content = response.choices[0].message.content.strip()
                assessment = json.loads(content)
                
                # 确保所有必需的字段都存在
                required_fields = ["score", "accuracy", "completeness", "technical_depth", 
                                 "clarity", "suggestions", "overall_comment"]
                for field in required_fields:
                    if field not in assessment:
                        if field == "score":
                            assessment[field] = 0
                        else:
                            assessment[field] = "未提供评价"
                
                # 根据答案长度和内容调整分数
                answer_length = len(answer.strip())
                if answer_length < 50:
                    assessment["score"] = min(assessment["score"], 30)
                    assessment["suggestions"] += "\n答案过短，需要更详细的说明。"
                
                return assessment
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                logger.error(f"Failed content: {content}")
                return {
                    "score": 0,
                    "accuracy": "系统错误，无法解析评估结果",
                    "completeness": "系统错误，无法解析评估结果",
                    "technical_depth": "系统错误，无法解析评估结果",
                    "clarity": "系统错误，无法解析评估结果",
                    "suggestions": "系统错误，无法解析评估结果",
                    "overall_comment": "系统错误，无法解析评估结果"
                }
                
        except Exception as e:
            logger.error(f"Error assessing answer: {str(e)}", exc_info=True)
            return {
                "score": 0,
                "accuracy": "评估过程出错",
                "completeness": "评估过程出错",
                "technical_depth": "评估过程出错",
                "clarity": "评估过程出错",
                "suggestions": "评估过程出错",
                "overall_comment": "评估过程出错"
            } 
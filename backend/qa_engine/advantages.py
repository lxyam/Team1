import os
import json
import dotenv
from typing import Dict, Any, List


class AdvantageQAGenerator:
    """
    一个用于根据候选人简历中的技能优势领域生成深度技术面试问题的类。
    """

    def __init__(self, client):
        """
        初始化 AdvantageQAGenerator。

        Args:
            client: 一个兼容 OpenAI SDK 接口的模型客户端对象。
        """
        self.model = "deepseek-chat"
        self.client = client

        self.system_prompt = """
        你是一个专业的面试官，请针对简历中明确列出的专业技术领域（如机器学习、分布式系统等），深入探究以下三个维度：
        1. 核心概念的技术原理掌握度
        2. 行业技术演进的关键认知
        3. 复杂技术问题的解决路径
        针对相关领域知识的具体细节进行提问。
        提出3个相关领域的技术性问题，采用如下JSON格式：
        [
            {
                "question": "问题内容",
                "purpose": "提问目的",
                "answer": "参考答案"
            },
            ...
        ]
        """

        self.interview_prompt = """
        你是一个专业的面试官，请分析候选人简历信息，从候选问题池中选择最适合的1个问题来面试候选人。
        返回JSON格式数据：
        {
            "question": "问题内容",
            "answer": "参考答案",
            "reason": "选择该问题的原因（需要结合候选人背景说明）"
        }
        """

    def generate_pool(self, resume_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        根据简历中的优势领域生成技术问题池。
        """
        try:
            context = {
                "skills": resume_data.get("skills", []),
                "advantages": resume_data.get("advantages", [])
            }
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": json.dumps(context, ensure_ascii=False)}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content.strip()
            return json.loads(content)

        except Exception as e:
            print(f"生成问题池失败: {e}")
            return []

    def select_question(self, resume_data: Dict[str, Any], questions_pool: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        根据候选人背景，从问题池中选择最合适的问题。
        """
        try:
            context = {
                "questions_pool": questions_pool,
                "candidate_info": {
                    "experience": resume_data.get("experience", []),
                    "education": resume_data.get("education", [])
                }
            }
            messages = [
                {"role": "system", "content": self.interview_prompt},
                {"role": "user", "content": json.dumps(context, ensure_ascii=False)}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content.strip()
            return json.loads(content)

        except Exception as e:
            print(f"选择问题失败: {e}")
            return {}

    def generate(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        主调用流程：生成问题池并选择最佳问题。
        """
        questions_pool = self.generate_pool(resume_data)
        selected_question = self.select_question(resume_data, questions_pool)
        return {
            "questions_pool": questions_pool,
            "selected_question": selected_question
        }


def advantages_main(resume_data: Dict[str, Any], client, out_path: str = None) -> Dict[str, Any]:
    """
    优势问题生成主入口。

    Args:
        resume_data: 简历结构化数据，要求含有 skills 和 advantages 字段。
        client: OpenAI 兼容客户端。
        out_path: 可选，将结果保存到的文件路径。

    Returns:
        选定的最合适的问题及其参考答案。
    """
    dotenv.load_dotenv()
    generator = AdvantageQAGenerator(client)
    result = generator.generate(resume_data)

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

    return result.get("selected_question", {})

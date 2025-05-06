import requests
import dotenv
import os
import json


class AdvantageQAGenerator:
    def __init__(self, **kwargs):
        self.url = kwargs.get("url", "https://api.siliconflow.cn/v1/chat/completions")
        self.token = kwargs.get("token", os.getenv("API_TOKEN"))
        self.model = kwargs.get("model", "Qwen/Qwen2.5-32B-Instruct")
        self.system_prompt = """你是一个专业的面试官，请针对简历中明确列出的专业技术领域（如机器学习、分布式系统等），深入探究以下三个维度：
        1. 核心概念的技术原理掌握度
        2. 行业技术演进的关键认知
        3. 复杂技术问题的解决路径针对相关领域知识的具体细节进行提问。
        提出3个相关领域的技术性问题，采用如下JSON格式：
        [
            {
                "question": "问题内容",
                "purpose": "提问目的",
                "answer": "参考答案",
            },
            ...
        ]
        """
        self.interview_prompt = """你是一个专业的面试官，请分析候选人简历信息，从候选问题池中选择最适合的1个问题来面试候选人。
        返回JSON格式数据：
        {
            "question": "问题内容",
            "answer": "参考答案",
            "reason": "选择该问题的原因（需要结合候选人背景说明）"
        }

        """

    def ask_api(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4096,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        response = requests.request("POST", self.url, json=payload, headers=headers)

        return response.json()

    def generate_pool(self, resume_json):
        context = {
            "skills": resume_json.get("skills", []),
            "advantages": resume_json.get("advantages", []),
        }
        questions_context = json.dumps(context, ensure_ascii=False)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": questions_context},
        ]
        response = json.loads(
            self.ask_api(messages)["choices"][0]["message"]["content"]
        )
        return response

    def select_question(self, resume_json, questions_pool):
        context = {
            "questions_pool": questions_pool,
            "candidate_info": {
                "experience": resume_json.get("experience", []),
                "education": resume_json.get("education", []),
            },
        }
        questions_context = json.dumps(context, ensure_ascii=False)
        messages = [
            {"role": "system", "content": self.interview_prompt},
            {"role": "user", "content": questions_context},
        ]
        response = json.loads(
            self.ask_api(messages)["choices"][0]["message"]["content"]
        )
        return response

    def generate(self, resume_json):
        questions_pool = self.generate_pool(resume_json)
        selected_question = self.select_question(resume_json, questions_pool)
        return {
            "questions_pool": questions_pool,
            "selected_question": selected_question,
        }


def advantages_main(resume_json, out_path=None):
    """
    优势问题生成的主接口函数。

    接收结构化的简历数据，生成问题池并从中选择最合适的问题。
    可以选择将结果保存到指定路径。

    Args:
        resume_json: json格式的简历结构化数据
        out_path: 可选，结果保存的文件路径。如果提供则将结果保存到该路径

    Returns:
        Dict[str, Any]: 返回选定的问题，包含question和answer字段
    """
    gen = AdvantageQAGenerator()
    res = gen.generate(resume_json)
    from pprint import pprint

    pprint(res)
    if out_path is not None:
        json.dump(
            res, open(out_path, "w", encoding="utf-8"), indent=4, ensure_ascii=False
        )
    return res["selected_question"]


if __name__ == "__main__":
    file_path = "../test/data/test_extractor.json"
    resume_json = json.load(open(file_path, "r"))
    advantages_main(resume_json, "../result/advantages/text_advantages.json")

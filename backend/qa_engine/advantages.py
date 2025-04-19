import requests
import dotenv
import os
import json


class AdvantageQAGenerator:
    def __init__(self, **kwargs):
        self.url = kwargs.get("url", "https://api.siliconflow.cn/v1/chat/completions")
        self.token = kwargs.get("token", os.getenv("API_TOKEN"))
        self.model = kwargs.get("model", "Qwen/Qwen2.5-32B-Instruct")
        self.system_prompt = """你是一个专业的面试官，请分析简历中的个人优势，对其进行评估并进行提问。提出3个问题，严格按照下面的JSON格式数据：
        [
            {
                "question": "问题内容",
                "purpose": "提问目的"
            },
            ...
        ]
        """
        self.interview_prompt = """你是一个专业的面试官，请分析候选人简历信息，从候选问题池中选择最适合的1个问题来面试候选人。
        返回JSON格式数据：
        {
            "question": "问题内容",
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
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

        response = requests.request("POST", self.url, json=payload, headers=headers)

        return response.json()

    def generate_pool(self, resume_json):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": str(resume_json["advantages"])},
        ]
        response = json.loads(self.ask_api(messages)["choices"][0]["message"]["content"])
        return response

    def select_question(self, resume_json, questions_pool):
        context = {
            "questions_pool": questions_pool,
            "candidate_info": {"skills": resume_json.get("skills", []), "experience": resume_json.get("experience", []), "education": resume_json.get("education", [])},
        }
        questions_context = json.dumps(context, ensure_ascii=False)
        messages = [
            {"role": "system", "content": self.interview_prompt},
            {"role": "user", "content": questions_context},
        ]
        response = json.loads(self.ask_api(messages)["choices"][0]["message"]["content"])
        return response

    def generate(self, resume_json):
        questions_pool = self.generate_pool(resume_json)
        selected_question = self.select_question(resume_json, questions_pool)
        return {
            "questions_pool": questions_pool,
            "selected_question": selected_question,
        }


if __name__ == "__main__":
    gen = AdvantageQAGenerator()
    file_path = "../test/data/test_extractor.json"
    resume_json = json.load(open(file_path, "r"))
    res = gen.generate(resume_json)
    from pprint import pprint

    pprint(res)
    out_path = "../result/advantages/text_advantages.json"
    json.dump(res, open(out_path, "w", encoding="utf-8"), indent=4, ensure_ascii=False)

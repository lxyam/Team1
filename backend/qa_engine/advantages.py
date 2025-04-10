import requests
import dotenv
import os
import json


class AdvantageQAGenerator:
    def __init__(self, **kwargs):
        self.url = kwargs.get("url", "https://api.siliconflow.cn/v1/chat/completions")
        self.token = kwargs.get("token", os.getenv("API_TOKEN"))
        self.model = kwargs.get("model", "Qwen/Qwen2.5-7B-Instruct")
        self.system_prompt = """你是一个专业的面试官，请分析简历内容，对个人优势进行评估，并进行提问。提出3个主问题，每个主问题下2个子问题。返回JSON格式数据：
        {
            "Q1": "第一个主问题"",
            "Q1.1": "第一个主问题的第一个子问题",
            "Q1.2":"第一个主问题的第二个子问题",
            ...
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

    def generate(self, resume_json):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": str(resume_json)},
        ]
        response = json.loads(self.ask_api(messages)["choices"][0]["message"]["content"])
        return response


if __name__ == "__main__":
    gen = AdvantageQAGenerator()
    file_path = "../test/data/test_extractor.json"
    resume_json = json.load(open(file_path, "r"))
    res = gen.generate(resume_json)
    from pprint import pprint

    pprint(res)
    out_path = "../test/data/text_advantages.json"
    json.dump(res, open(out_path, "w", encoding="utf-8"), indent=4, ensure_ascii=False)

import json

class InterviewManager:
    def __init__(self, client):
        self.client = client
        self.model = "deepseek-chat"

        self.reference_prompt = """
        你是一个面试官，面前有一个求职者，基于以下问题，请生成一个完整、专业且符合标准的参考答案。请确保参考答案既真实又符合行业标准。
        
        要求：
        - 提供详细的技术实现细节
        - 展示对项目难点和解决方案的深入理解
        - 体现良好的技术思维和表达能力
        - 用自然口语表达，保持逻辑清晰，避免书面语
        """

        self.evaluation_prompt = """
        你是一个面试官，负责对求职者的回答进行评分和评估。请从以下四个方面进行打分和详细分析：
        
        1. **技术深度**：是否展现了对技术细节的掌握和理解  
        2. **表达能力**：回答是否逻辑清晰、语言流畅、表达准确  
        3. **项目理解**：是否准确描述项目目标、架构和关键技术点  
        4. **问题解决能力**：是否展示出分析问题、解决问题的思路和执行力  
        
        请按以下标准对每项进行评分（A/B/C/D）：
        - A：非常优秀 —— 回答全面、深入，技术细节丰富，条理清晰  
        - B：良好 —— 回答清晰，有一定深度，但仍可补充更详细的内容  
        - C：一般 —— 回答基本完整，但缺乏技术细节或逻辑性不强  
        - D：不合格 —— 回答模糊、内容错误或完全缺乏相关信息  
        
        请用如下JSON格式返回：
        {
            "技术深度": {"评分": "A", "理由": "回答详细，深入解释了XXX的实现"},
            "表达能力": {"评分": "B", "理由": "整体表达顺畅，但略显抽象"},
            "项目理解": {"评分": "A", "理由": "清晰描述了架构与核心目标"},
            "问题解决能力": {"评分": "B", "理由": "能提出方案，但缺乏具体实现说明"},
            "总评": {"评分": "A", "理由": "整体回答专业、表达自然，体现了较强能力"}
        }
        """

    def generate_reference_answer(self, question):
        messages = [
            {"role": "system", "content": self.reference_prompt},
            {"role": "user", "content": f"问题：{question}\n请生成一个高质量的参考答案。"}
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content.strip()

    def grade_and_evaluate(self, user_answer, reference_answer):
        prompt = f"""
        用户回答：
        {user_answer}
        
        参考答案：
        {reference_answer}
        
        请对用户的回答进行评分。
        """
        messages = [
            {"role": "system", "content": self.evaluation_prompt},
            {"role": "user", "content": prompt}
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content.strip()


def evaluation(client, projects, advantages, code, user_answers: dict):
    manager = InterviewManager(client)
    report = {"projects": [], "advantages": {}, "code": {}}

    # 1. 项目评估
    for project_name, qa_list in projects.items():
        for qa in qa_list:
            question = qa["question"]
            user_answer = qa["answer"]
            reference_answer = manager.generate_reference_answer(question)
            evaluation = manager.grade_and_evaluate(user_answer, reference_answer)
            report["项目问答"].append({
                "项目名": project_name,
                "问题": question,
                "参考答案": reference_answer,
                "用户回答": user_answer,
                "评估": json.loads(evaluation)
            })

    # 2. 优势评估
    if advantages:
        question = advantages["question"]
        user_answer = advantages["answer"]
        reference_answer = manager.generate_reference_answer(question)
        evaluation = manager.grade_and_evaluate(user_answer, reference_answer)
        report["优势问答"] = {
            "问题": question,
            "参考答案": reference_answer,
            "用户回答": user_answer,
            "评估": json.loads(evaluation)
        }

    # 3. 编程题评估
    if code:
        question, user_answer = code
        reference_answer = manager.generate_reference_answer(question)
        evaluation = manager.grade_and_evaluate(user_answer, reference_answer)
        report["编程题"] = {
            "问题": question,
            "参考答案": reference_answer,
            "用户回答": user_answer,
            "评估": json.loads(evaluation)
        }

    return report

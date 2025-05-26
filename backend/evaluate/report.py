import json

class InterviewManager:
    def __init__(self, client):
        self.client = client
        self.model = "deepseek-chat"

        self.reference_prompt = """
        作为面试官，请基于以下问题生成一个完整、专业且符合标准的参考答案。确保答案既真实又符合行业标准。
        
        注意：
        1. 不要使用任何特殊符号或标记（如 **, ---, # 等）
        2. 不要使用 markdown 格式
        3. 使用纯文本格式，可以用数字或中文符号标记列表
        4. 段落之间用换行分隔
        
        答案要求：
        1. 提供详细的技术实现细节
        2. 展示对项目难点和解决方案的深入理解
        3. 体现良好的技术思维和表达能力
        4. 用自然口语表达，保持逻辑清晰，避免书面语
        """

        self.evaluation_prompt = """
        作为面试官，负责对求职者的回答进行评分和评估。你必须严格按照指定的JSON格式返回评估结果，不要添加任何其他内容。

        评分标准：
        1. 技术深度：是否展现了对技术细节的掌握和理解
        2. 表达能力：回答是否逻辑清晰、语言流畅、表达准确
        3. 项目理解：是否准确描述项目目标、架构和关键技术点
        4. 问题解决能力：是否展示出分析问题、解决问题的思路和执行力

        评分等级（A/B/C/D）：
        A：非常优秀 - 回答全面、深入，技术细节丰富，条理清晰
        B：良好 - 回答清晰，有一定深度，但仍可补充更详细的内容
        C：一般 - 回答基本完整，但缺乏技术细节或逻辑性不强
        D：不合格 - 回答模糊、内容错误或完全缺乏相关信息

        你必须返回如下格式的JSON，不要添加任何其他内容：
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
        
        请对用户的回答进行评分。请严格按照以下JSON格式返回，不要添加任何其他内容：
        {{
            "技术深度": {{"评分": "A", "理由": "回答详细，深入解释了XXX的实现"}},
            "表达能力": {{"评分": "B", "理由": "整体表达顺畅，但略显抽象"}},
            "项目理解": {{"评分": "A", "理由": "清晰描述了架构与核心目标"}},
            "问题解决能力": {{"评分": "B", "理由": "能提出方案，但缺乏具体实现说明"}},
            "总评": {{"评分": "A", "理由": "整体回答专业、表达自然，体现了较强能力"}}
        }}
        """
        messages = [
            {"role": "system", "content": self.evaluation_prompt},
            {"role": "user", "content": prompt}
        ]
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            evaluation_text = response.choices[0].message.content.strip()
            print(f"Debug - Raw response from AI: {evaluation_text}")  # 添加调试信息
            
            # 清理 Markdown 代码块标记
            if evaluation_text.startswith("```json"):
                evaluation_text = evaluation_text[7:]  # 移除 ```json
            if evaluation_text.endswith("```"):
                evaluation_text = evaluation_text[:-3]  # 移除结尾的 ```
            evaluation_text = evaluation_text.strip()
            
            # 尝试解析 JSON
            evaluation_json = json.loads(evaluation_text)
            
            # 验证 JSON 结构
            required_keys = ["技术深度", "表达能力", "项目理解", "问题解决能力", "总评"]
            for key in required_keys:
                if key not in evaluation_json:
                    raise ValueError(f"Missing required key: {key}")
                if "评分" not in evaluation_json[key] or "理由" not in evaluation_json[key]:
                    raise ValueError(f"Invalid structure for key: {key}")
                if evaluation_json[key]["评分"] not in ["A", "B", "C", "D"]:
                    raise ValueError(f"Invalid score for key: {key}")
            
            return evaluation_text
        except Exception as e:
            print(f"Debug - Error type: {type(e)}")  # 添加错误类型信息
            print(f"Debug - Error message: {str(e)}")  # 添加错误信息
            # 返回一个默认的评估结果
            default_evaluation = {
                "技术深度": {"评分": "B", "理由": "评估解析失败，返回默认评分"},
                "表达能力": {"评分": "B", "理由": "评估解析失败，返回默认评分"},
                "项目理解": {"评分": "B", "理由": "评估解析失败，返回默认评分"},
                "问题解决能力": {"评分": "B", "理由": "评估解析失败，返回默认评分"},
                "总评": {"评分": "B", "理由": "评估解析失败，返回默认评分"}
            }
            return json.dumps(default_evaluation, ensure_ascii=False)


def evaluation(client, projects, advantages, code, user_answers: dict):
    manager = InterviewManager(client)
    report = {"project_qa": [], "advantages": {}, "code": {}}

    # 用于存储已经出现过的改进建议
    seen_improvements = set()

    # 1. 项目评估
    for project_name, qa_list in projects.items():
        for qa in qa_list:
            try:
                question = qa["question"]
                user_answer = qa["answer"]
                reference_answer = manager.generate_reference_answer(question)
                evaluation = manager.grade_and_evaluate(user_answer, reference_answer)
                eval_dict = json.loads(evaluation)
                
                # 去重改进建议
                for category in eval_dict:
                    if eval_dict[category]["评分"] in ["C", "D"]:
                        improvement_key = f"{category}: {eval_dict[category]['理由']}"
                        if improvement_key not in seen_improvements:
                            seen_improvements.add(improvement_key)
                        else:
                            # 如果已经存在相同类型的建议，移除当前的
                            eval_dict[category]["理由"] = ""
                
                report["project_qa"].append({
                    "project_name": project_name,
                    "question": question,
                    "reference_answer": reference_answer,
                    "user_answer": user_answer,
                    "evaluation": eval_dict
                })
            except Exception as e:
                print(f"Warning: Error processing project QA: {e}")
                continue

    # 2. 优势评估
    if advantages:
        try:
            question = advantages["question"]
            user_answer = advantages["answer"]
            reference_answer = manager.generate_reference_answer(question)
            evaluation = manager.grade_and_evaluate(user_answer, reference_answer)
            eval_dict = json.loads(evaluation)
            
            # 去重改进建议
            for category in eval_dict:
                if eval_dict[category]["评分"] in ["C", "D"]:
                    improvement_key = f"{category}: {eval_dict[category]['理由']}"
                    if improvement_key not in seen_improvements:
                        seen_improvements.add(improvement_key)
                    else:
                        # 如果已经存在相同类型的建议，移除当前的
                        eval_dict[category]["理由"] = ""
            
            report["advantages"] = {
                "question": question,
                "reference_answer": reference_answer,
                "user_answer": user_answer,
                "evaluation": eval_dict
            }
        except Exception as e:
            print(f"Warning: Error processing advantages: {e}")

    # 3. 编程题评估
    if code:
        try:
            question, user_answer = code
            reference_answer = manager.generate_reference_answer(question)
            evaluation = manager.grade_and_evaluate(user_answer, reference_answer)
            report["code"] = {
                "question": question,
                "reference_answer": reference_answer,
                "user_answer": user_answer,
                "evaluation": json.loads(evaluation)
            }
        except Exception as e:
            print(f"Warning: Error processing code: {e}")

    return report

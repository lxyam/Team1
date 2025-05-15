import os
import json
from dotenv import load_dotenv
from qa_engine.projects import ProjectQAGenerator
from openai import OpenAI

# Function to simulate user interaction and grading

class InterviewManager:
    def __init__(self, **kwargs):
        # Load API configuration from environment variables or kwargs
        self.api_key = kwargs.get("api_key", os.getenv("OPENAI_API_KEY"))
        self.api_base = kwargs.get("api_base", os.getenv("OPENAI_API_BASE"))
        self.model = kwargs.get("model", "deepseek-chat")

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)

        # Define system prompts
        self.reference_prompt = """
        你是一个面试官，面前有一个求职者，基于以下问题，请生成一个完整、专业且符合标准的参考答案。请确保参考答案既真实又符合行业标准。

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

        self.evaluation_prompt = """
        你是一个面试官，负责对求职者的回答进行评分和评估。请从以下几个方面对用户的回答进行详细评估：

        1. **技术深度**：考察对技术细节的理解和掌握程度。用户是否能够准确地描述相关技术，展示出对细节的深入理解？
        2. **表达能力**：考察回答的清晰度和逻辑性。用户是否能够条理清晰、结构合理地表达自己的观点？
        3. **项目理解**：考察对项目整体架构和关键点的把握。用户是否能准确描述项目的目标、架构及实现细节？
        4. **问题解决**：考察展示的问题分析和解决能力。用户是否能够清晰地分析问题并提出合理的解决方案？

        请对每个方面给出以下的评分（A、B、C、D）以及详细的评分理由：
        - **A**：非常优秀，回答全面且深刻，展现了出色的能力。
        - **B**：良好，回答有一定深度，但仍有改进的空间。
        - **C**：一般，回答较为基础，缺乏深度或有明显的不足。
        - **D**：不合格，回答未能满足基本要求，存在重大问题。

        最后，请给出对整体回答的总体评价（A、B、C、D），并提供综合评价理由。
        """


    def generate_reference_answer(self, question):
        # Generate reference answer
        prompt = f"Question: {question}\nPlease provide a reference answer."
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.reference_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        reference_answer = response.choices[0].message.content.strip()
        return reference_answer

    def grade_and_evaluate(self, user_answer, reference_answer):
        # Generate grading and evaluation
        prompt = f"User Answer: {user_answer}\nReference Answer: {reference_answer}\n\nPlease grade the user's response based on the following aspects:\n1. 技术深度\n2. 表达能力\n3. 项目理解\n4. 问题解决\n\nGrade the user's response (A, B, C, D) for each aspect, and provide an overall evaluation along with reasons."
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.evaluation_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        evaluation = response.choices[0].message.content.strip()
        return evaluation


def user_interaction():
    print("请输入你的回答")
    user_answer = input("Your Answer: ")
    return user_answer


def save_results_to_file(results, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)


def interact_and_grade(result):
    manager = InterviewManager()
    all_results = []

    for project_name, project_data in result.items():
        print(f"\nProject: {project_name}")
        selected_questions_data = project_data.get('selected_questions', {}).get('selected_questions', [])

        if selected_questions_data:
            question_data = selected_questions_data[0]
            question = question_data.get("question")
            reason = question_data.get("reason")

            print(f"\nQuestion: {question}")
            print(f"Reason: {reason}")

            # Generate reference answer
            reference_answer = manager.generate_reference_answer(question)
            print(f"Reference Answer: {reference_answer}")

            # Simulate user answer
            user_answer = user_interaction()

            # Grade and evaluate
            evaluation = manager.grade_and_evaluate(user_answer, reference_answer)
            print(f"Evaluation: {evaluation}")

            # Collect results
            all_results.append({
                "Project": project_name,
                "Question": question,
                "Reason": reason,
                "Reference Answer": reference_answer,
                "Your Answer": user_answer,
                "Evaluation": evaluation
            })
        else:
            print("Error: 'selected_questions' is empty or missing.")

    # Save all results to a file
    result_dir = os.path.join(os.path.dirname(__file__), "result")
    os.makedirs(result_dir, exist_ok=True)
    out_path = os.path.join(result_dir, "evaluation_results.json")
    save_results_to_file(all_results, out_path)


def main():
    # Load environment variables
    load_dotenv()

    # Initialize the generator
    generator = ProjectQAGenerator()

    # Load resume data
    file_path = os.path.join(os.path.dirname(__file__), "test/data/test_extractor.json")
    with open(file_path, "r", encoding="utf-8") as f:
        resume_data = json.load(f)

    # Generate questions
    result = generator.generate_for_resume(resume_data)
    print(result)

    # Interact with user and grade answers
    interact_and_grade(result)


if __name__ == "__main__":
    main()

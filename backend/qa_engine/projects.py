import dotenv
import os
import json
from typing import Dict, Any, List
from openai import OpenAI


class ProjectQAGenerator:
    """
    一个用于根据简历中的项目经历生成面试问题和参考答案的类。

    该类使用 OpenAI API 来生成问题、选择问题和生成答案。
    它包含以下主要功能：
    - 根据单个项目信息生成一系列面试问题。
    - 根据候选人背景从问题池中选择最合适的问题。
    - 为选定的问题生成优秀的口语化参考答案。
    - 处理整个简历，为所有项目生成问题和答案。
    """
    def __init__(self, **kwargs):
        """
        初始化 ProjectQAGenerator。

        Args:
            **kwargs: 关键字参数，用于覆盖默认配置或环境变量。
                api_key (str, optional): OpenAI API 密钥。默认为环境变量 OPENAI_API_KEY。
                api_base (str, optional): OpenAI API 基础 URL。默认为环境变量 OPENAI_API_BASE。
                model (str, optional): 使用的 OpenAI 模型。默认为 "deepseek-chat"。
        """
        # 从环境变量或kwargs加载API配置
        self.api_key = kwargs.get("api_key", os.getenv("OPENAI_API_KEY"))
        self.api_base = kwargs.get("api_base", os.getenv("OPENAI_API_BASE"))
        self.model = kwargs.get("model", "deepseek-chat")
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )
        
        # 系统提示词
        self.system_prompt = """
        你是一个专业的技术面试官，正在面试一位候选人。请根据候选人简历中的项目经历，生成一系列专业的面试问题。
        
        请生成以下两类问题：
        1. 项目基础问题：关于项目背景、技术选型、架构设计等基础问题
        2. 技术深度问题：针对项目中使用的核心技术提出的深度问题
        3. 挑战与解决方案问题：关于项目中遇到的挑战和解决方案的问题
        
        对于每个项目，请生成至少3个问题，并确保问题具有针对性和专业性。
        
        返回JSON格式数据：
        {
            "project_name": "项目名称",
            "questions": [
                {
                    "question": "问题内容",
                    "type": "问题类型(基础/技术/挑战)",
                    "purpose": "提问目的"
                },
                ...
            ]
        }
        """
        
        # 面试官选择问题的系统提示词
        self.interviewer_prompt = """
        你是一位经验丰富的技术面试官，需要从候选问题池中选择最适合的问题来面试候选人。
        
        请根据候选人的背景信息（包括技能、工作经验和教育背景）选择问题，遵循以下原则：
        1. 问题应该与候选人的技术栈和专业领域相匹配
        2. 问题应该考虑候选人的工作经验水平
        3. 问题应该能够验证候选人在简历中声明的技能
        4. 问题应该有层次性，从基础到深入
        5. 问题应该能够揭示候选人在项目中的实际贡献和解决问题的能力
        6. 避免选择与候选人背景不相关的问题
        
        请从候选问题池中选择1个最适合的问题。
        
        返回JSON格式数据：
        {
            "selected_questions": [
                {
                    "question": "问题内容",
                    "reason": "选择该问题的原因（需要结合候选人背景说明）"
                },
                ...
            ]
        }
        """

    def generate_questions(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据项目数据生成面试问题
        
        Args:
            project_data: 项目数据，包含name, description, technologies, responsibilities, achievements等字段
            
        Returns:
            包含问题列表的字典
        """
        try:
            # 构建项目上下文
            project_context = f"""
            项目名称：{project_data.get('name', '')}
            项目描述：{project_data.get('description', '')}
            使用技术：{', '.join(project_data.get('technologies', []))}
            项目职责：{', '.join(project_data.get('responsibilities', []))}
            项目成就：{', '.join(project_data.get('achievements', []))}
            """
            
            # 调用API生成问题
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": project_context}
                ],
                response_format={"type": "json_object"}
            )
            
            # 解析响应
            content = response.choices[0].message.content.strip()
            questions_data = json.loads(content)
            
            return questions_data
            
        except Exception as e:
            print(f"生成问题失败: {e}")
            return 0
    
    def select_questions(self, questions_pool: Dict[str, Any], resume_data: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
        """
        从问题池中选择最适合的问题
        
        Args:
            questions_pool: 问题池，包含project_name和questions字段
            resume_data: 候选人的简历数据
            
        Returns:
            包含选定问题的字典
        """
        try:
            # 构建问题池和简历上下文
            context = {
                "questions_pool": questions_pool,
                "candidate_info": {
                    "skills": resume_data.get("skills", []),
                    "experience": resume_data.get("experience", []),
                    "education": resume_data.get("education", [])
                }
            }
            questions_context = json.dumps(context, ensure_ascii=False)
            
            # 调用API选择问题
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.interviewer_prompt},
                    {"role": "user", "content": f"请根据候选人的背景信息，从问题池中选择最适合的问题:\n{questions_context}"}
                ],
                response_format={"type": "json_object"}
            )
            
            # 解析响应
            content = response.choices[0].message.content.strip()
            selected_questions = json.loads(content)
            
            return selected_questions
            
        except Exception as e:
            print(f"选择问题失败: {e}")


    def generate_for_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        为简历中的所有项目生成问题并选择最佳问题
        
        Args:
            resume_data: 简历数据，包含projects字段
            
        Returns:
            包含所有项目问题的字典
        """
        result = {}
        
        # 获取简历中的项目列表
        projects = resume_data.get("projects", [])
        
        for project in projects:
            # 为每个项目生成问题
            questions_pool = self.generate_questions(project)
            # 从问题池中选择最佳问题
            selected_questions = self.select_questions(questions_pool, resume_data)
            # 兼容 selected_questions 结构
            selected_q_list = selected_questions.get("selected_questions", []) if isinstance(selected_questions, dict) else selected_questions
            # 生成每个问题的优秀口语化参考答案
            answers = self.generate_ans(project, selected_q_list)
            # 将结果添加到结果字典中
            result[project.get("name", "未知项目")] = {
                "questions_pool": questions_pool,
                "selected_questions": selected_questions,
                "answers": answers
            }
        
        return result

    def generate_ans(self, project_data: Dict[str, Any], selected_questions: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        根据项目数据和已选定的问题，生成每个问题的优秀口语化参考答案
        Args:
            project_data: 项目数据，包含name, description, technologies, responsibilities, achievements等字段
            selected_questions: 已选定的问题列表，每项包含question字段
        Returns:
            包含每个问题及其参考答案的列表
        """
        answers = []
        for q in selected_questions:
            try:
                # 构建上下文
                context = f"""
                你是一位正在参加技术面试的优秀候选人。请针对以下项目经历和面试官提出的问题，给出一个自然流畅、口语化、能打动面试官的高水平回答（不要书面语）：\n\n项目名称：{project_data.get('name', '')}\n项目描述：{project_data.get('description', '')}\n使用技术：{', '.join(project_data.get('technologies', []))}\n项目职责：{', '.join(project_data.get('responsibilities', []))}\n项目成就：{', '.join(project_data.get('achievements', []))}\n\n面试问题：{q.get('question', '')}\n"""
                system_prompt = "你是一位优秀的技术应聘者，请用自然、流畅、口语化的表达方式，回答面试官的问题，突出你的专业能力、项目贡献和沟通能力，避免书面语和模板化。答案要简洁有逻辑，能让面试官留下深刻印象。只返回答案内容，不要添加任何说明。"
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": context}
                    ],
                    response_format={"type": "text"}
                )
                answer = response.choices[0].message.content.strip()
                answers.append({"question": q.get("question", ""), "answer": answer})
            except Exception as e:
                answers.append({"question": q.get("question", ""), "answer": f"生成答案失败: {e}"})
        return answers

def projects_main(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    项目问题生成的主接口函数。

    接收结构化的简历数据，为简历中的每个项目生成问题池、
    从中选择最合适的问题，并生成这些问题的参考答案。

    Args:
        resume_data: json格式的简历结构化数据，需要包含 'projects' 字段。

    Returns:
        {"项目名称": 
            [{
            "question": "content",
            "answer": "content" 
            }]
        }
    """
    # 加载环境变量 (例如 OPENAI_API_KEY, OPENAI_API_BASE)
    dotenv.load_dotenv()

    # 初始化问题生成器实例
    generator = ProjectQAGenerator()

    # 为简历中的所有项目生成问题、选择问题并生成答案
    results = generator.generate_for_resume(resume_data)

    # 初始化用于存储最终结果的字典
    final_a = {} # 存储每个项目问题的答案

    # 遍历生成器返回的结果，提取每个项目的选定问题和答案
    for project_name, project_data in results.items():
        # 检查是否存在选定的问题和答案
        if "selected_questions" in project_data and "answers" in project_data:
            # 提取问题和答案列表
            final_a[project_name] = project_data["answers"]
        else:
            # 如果没有选定问题或答案，则设置为空列表
            final_a[project_name] = []

    # 返回包含所有项目选定问题和答案的两个字典
    return final_a

if __name__ == "__main__":
    # 加载测试数据
    file_path = os.path.join(os.path.dirname(__file__), "../test/data/test_extractor.json")
    with open(file_path, "r", encoding="utf-8") as f:
        resume_data = json.load(f)

    print(projects_main(resume_data))


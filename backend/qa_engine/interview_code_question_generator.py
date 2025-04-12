import json
import os
import httpx
import datetime
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

class QuestionDifficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

@dataclass
class TechnologyStack:
    ml_frameworks: List[str]
    databases: List[str]
    programming_languages: List[str]
    backend_frameworks: List[str]
    big_data_tools: List[str]

@dataclass
class CodingQuestion:
    title: str
    difficulty: QuestionDifficulty
    description: str
    requirements: List[str]
    example_input: str
    example_output: str
    solution: str
    test_cases: List[Dict[str, Any]]
    technologies: List[str]
    key_points: List[str]

@dataclass
class APIConfig:
    """API配置类"""
    api_key: str
    api_base: str
    model: str
    temperature: float    # 移除了 timeout 和 max_retries

    @classmethod
    def from_env(cls) -> 'APIConfig':
        """从环境变量加载API配置"""
        return cls(
            api_key=os.getenv("OPENAI_API_KEY"),
            api_base=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("API_TEMPERATURE", "0.7"))
        )

class InterviewQuestionGenerator:
    def __init__(self):
        # 从环境变量加载配置
        self.config = APIConfig.from_env()
        # print(f"API Key: {self.config.api_key}, Base URL: {self.config.api_base}")
        # 简化 OpenAI 客户端配置
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.api_base
        )

        # 只保存 temperature 配置
        self.temperature = self.config.temperature

    def _categorize_skills(self, skills: List[str]) -> TechnologyStack:
        """将技能分类到不同的技术领域"""
        ml_frameworks = ["TensorFlow", "PyTorch", "Keras", "XGBoost", "LightGBM"]
        databases = ["PostgreSQL", "MySQL", "MongoDB", "Cassandra", "Elasticsearch"]
        programming_languages = ["Python", "JavaScript", "C++", "Java"]
        backend_frameworks = ["FastAPI", "Flask", "Django"]
        big_data_tools = ["Apache Spark", "Hadoop", "Kafka", "Flink"]

        return TechnologyStack(
            ml_frameworks=[s for s in skills if s in ml_frameworks],
            databases=[s for s in skills if s in databases],
            programming_languages=[s for s in skills if s in programming_languages],
            backend_frameworks=[s for s in skills if s in backend_frameworks],
            big_data_tools=[s for s in skills if s in big_data_tools]
        )

    def generate_question_prompt(self, tech_stack: TechnologyStack, difficulty: QuestionDifficulty) -> str:
        """生成用于获取面试题的提示"""
        return f"""
        请生成一道结合以下技术栈的编程面试题：

        编程语言：{', '.join(tech_stack.programming_languages)}
        后端框架：{', '.join(tech_stack.backend_frameworks)}
        数据库：{', '.join(tech_stack.databases)}
        机器学习框架：{', '.join(tech_stack.ml_frameworks)}
        大数据工具：{', '.join(tech_stack.big_data_tools)}

        要求：
        1. 难度级别：{difficulty.value}
        2. 题目应该结合实际工作场景
        3. 需要包含完整的问题描述、要求、示例输入输出、解决方案和测试用例
        4. 解决方案应该包含详细的代码实现和注释
        5. 应该覆盖多个技术点的结合

        请以JSON格式返回，包含以下字段：
        - title: 题目标题
        - difficulty: 难度级别
        - description: 问题描述
        - requirements: 具体要求（数组）
        - example_input: 示例输入
        - example_output: 示例输出
        - solution: 完整的解决方案代码
        - test_cases: 测试用例数组
        - technologies: 涉及的技术（数组）
        - key_points: 考察要点（数组）
        """

    def generate_interview_question(self, skills: List[str], difficulty: QuestionDifficulty) -> Tuple[CodingQuestion, str]:
        """生成面试编程题，返回处理后的问题对象和原始响应"""
        tech_stack = self._categorize_skills(skills)
        prompt = self.generate_question_prompt(tech_stack, difficulty)

        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "你是一位经验丰富的技术面试官，专注于生成高质量的编程面试题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature
            )
            
            # 获取原始响应内容
            content = response.choices[0].message.content.strip()
            
            # 移除可能存在的 Markdown 代码块标记
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            # 尝试解析为结构化数据
            try:
                question_data = json.loads(content.strip())
                return CodingQuestion(**question_data), content
            except json.JSONDecodeError as je:
                print(f"JSON解析错误: {str(je)}")
                print(f"原始内容: {content}")
                return None, content

        except Exception as e:
            print(f"API调用错误: {str(e)}")
            return None, ""

    def save_question_to_file(self, question: CodingQuestion, filename: str):
        """将生成的面试题保存到文件"""
        output_dir = os.path.join(os.path.dirname(__file__), "../result/code_responses")
        os.makedirs(output_dir, exist_ok=True)
        
        file_path = os.path.join(output_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(question.__dict__, f, ensure_ascii=False, indent=2)
        
        print(f"面试题已保存到: {file_path}")

    def save_raw_response(self, content: str, difficulty: str):
        """保存原始响应内容"""
        output_dir = os.path.join(os.path.dirname(__file__), "../result/code_responses")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(output_dir, f"code_response_{difficulty}_{timestamp}.txt")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"原始响应已保存到: {file_path}")

def main():
    # 从JSON文件加载技能列表
    with open("../test/data/test_extractor.json", 'r', encoding='utf-8') as f:
        resume_data = json.load(f)
    
    skills = resume_data.get("skills", [])
    
    # 创建生成器实例
    generator = InterviewQuestionGenerator()
    
    # 生成不同难度的面试题
    for difficulty in QuestionDifficulty:
        question, raw_response = generator.generate_interview_question(skills, difficulty)
        
        # 保存原始响应
        if raw_response:
            generator.save_raw_response(raw_response, difficulty.value)
        
        # 保存结构化数据
        if question:
            generator.save_question_to_file(
                question,
                f"code_question_{difficulty.value}.json"
            )

if __name__ == "__main__":
    main()
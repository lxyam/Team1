'''
根据skills字段生成编程有关问题。
.env设置在了../.env,需要修改对应的路径，19行
实现函数为
generate_interview_question(resume_file_path: str) -> Tuple[str, str]:
输入为简历文件路径，输出为问题和答案
'''

import json
from typing import Dict, List, Tuple
from openai import OpenAI  # 修改导入方式
import random
from dotenv import load_dotenv
import os
from pathlib import Path

class CodeQuestionGenerator:
    def __init__(self, client):
        """初始化代码问题生成器，从.env文件加载配置"""
        # 加载.env文件
        env_path = '../.env'
        load_dotenv(env_path)
        
        # 设置OpenAI配置
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_base = os.getenv('OPENAI_API_BASE')
        
        # 初始化OpenAI客户端
        self.client = client
        
        # 加载其他配置
        self.model = 'deepseek-chat'
        self.temperature = float(os.getenv('API_TEMPERATURE', 0.7))
        self.timeout = int(os.getenv('API_TIMEOUT', 30))
        self.max_retries = int(os.getenv('API_MAX_RETRIES', 3))

    def _extract_skills(self, resume_data: Dict) -> List[str]:
        """从简历数据中提取技术技能
        
        Args:
            resume_data (Dict): 简历JSON数据
            
        Returns:
            List[str]: 技术技能列表
        """
        return resume_data.get("skills", [])

    def _generate_questions(self, skills: List[str]) -> List[Dict]:
        """使用LLM生成基于技能的编程问题
        
        Args:
            skills (List[str]): 技术技能列表
            
        Returns:
            List[Dict]: 问题和答案的列表
        """
        prompt = f"""基于以下技术技能生成3个具有挑战性的编程问题和答案：
        技能: {', '.join(skills)}
        
        每个问题应该：
        1. 涉及实际编程场景
        2. 需要综合运用多个技能
        3. 包含完整的参考答案
        4. 用中文描述问题
        
        按以下格式返回JSON：
        [
            {{"question": "问题描述", "answer": "详细答案"}}
        ]
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的编程面试官。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature
            )
            # 修改响应处理方式
            content = response.choices[0].message.content
            if not content:
                print("API返回空响应")
                return []
                
            try:
                # 移除可能存在的Markdown代码块标记
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]  # 移除开头的```json
                if content.endswith("```"):
                    content = content[:-3]  # 移除结尾的```
                    
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {str(e)}\n响应内容: {content}")
                return []
                
        except Exception as e:
            print(f"生成问题时发生错误: {str(e)}")
            return []

    def _select_best_question(self, question_pool: List[Dict], skills: List[str]) -> Dict:
        """使用LLM从问题池中选择最合适的问题
        
        Args:
            question_pool (List[Dict]): 候选问题池
            skills (List[str]): 技能列表
            
        Returns:
            Dict: 选中的问题和答案
        """
        questions_text = "\n".join([
            f"问题{i+1}: {q['question']}\n答案{i+1}: {q['answer']}" 
            for i, q in enumerate(question_pool)
        ])
        
        prompt = f"""作为面试专家,请从以下三个编程问题中选择一个最合适的问题。
        考虑以下因素:
        1. 问题难度适中
        2. 能够综合考察多个技能: {', '.join(skills)}
        3. 问题描述清晰,答案完整
        
        候选问题:
        {questions_text}
        
        请只返回选中的问题编号(1,2或3)
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的技术面试专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3  # 使用较低的temperature以获得更确定的选择
            )
            
            # 解析返回的问题编号
            selected_num = int(response.choices[0].message.content.strip()) - 1
            return question_pool[selected_num]
        except Exception as e:
            print(f"选择问题时发生错误: {str(e)}")
            return random.choice(question_pool)  # 发生错误时随机选择

    def get_question(self, resume_json: Dict) -> Tuple[str, str]:
        """从简历生成一个编程问题
        
        Args:
            resume_json (Dict): 简历JSON数据
            
        Returns:
            Tuple[str, str]: (选中的问题, 参考答案)
        """
        # 提取技能
        skills = self._extract_skills(resume_json)
        
        # 生成问题池
        question_pool = self._generate_questions(skills)
        
        # 如果生成失败或问题池为空，返回默认问题
        if not question_pool:
            return ("请实现一个简单的REST API服务器", 
                   "可以使用Flask或FastAPI实现一个基本的CRUD API服务")
        
        # 使用LLM选择最合适的问题
        selected = self._select_best_question(question_pool, skills)
        return selected["question"], selected["answer"]

def generate_interview_code_question(resume_data, client) -> Tuple[str, str]:
    """从JSON格式的简历生成编程面试问题的API接口

    Args:
        resume_file_path (str): 简历JSON
            
    Returns:
        Tuple[str, str]: (问题, 参考答案)的元组
        
    Raises:
        FileNotFoundError: 找不到简历文件时
        json.JSONDecodeError: JSON格式无效时
        ValueError: 简历数据缺少必要字段时
    """
    try:
        
        # 验证skills字段
        if "skills" not in resume_data:
            raise ValueError("简历数据中必须包含'skills'字段")
            
        # 使用现有的生成器获取问题
        generator = CodeQuestionGenerator(client)
        return generator.get_question(resume_data)

    except json.JSONDecodeError:
        print(f"错误: {resume_data} 不是有效的JSON格式")
        raise
    except Exception as e:
        print(f"生成问题时发生错误: {str(e)}")
        return ("请实现一个简单的REST API服务器", 
                "可以使用Flask或FastAPI实现一个基本的CRUD API服务")

# 修改使用示例
if __name__ == "__main__":
    try:
        # 指定文件路径
        resume_path = "../test/data/test_extractor.json"
        output_path = "../result/code_responses/code_responses.json"
        
        # 创建输出目录(如果不存在)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 调用API接口
        question, answer = generate_interview_code_question(resume_path)
        
        # 构建输出的JSON数据
        output_data = {
            "code_question": {
                "question": question,
                "answer": answer
            }
        }
        
        # 将结果保存到JSON文件
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"问题和答案已保存到: {output_path}")
        
    except Exception as e:
        print(f"程序执行出错: {str(e)}")

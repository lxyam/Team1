from typing import List, Dict, Any
from .item_enhanced import ProjectQAGenerator as EnhancedProjectQAGenerator

class ProjectQAGenerator(EnhancedProjectQAGenerator):
    """项目问答生成器
    
    继承自增强版问答生成器，提供更强大的问答生成功能：
    1. 多轮追问机制 - 支持主问题和相关追问的组合
    2. 细化的评分维度 - 包括技术理解、实践经验、解决方案和表达能力
    3. 项目类型识别 - 根据技术栈自动判断项目类型
    4. 智能答案生成 - 基于项目背景生成专业、全面的标准答案
    """
    def __init__(self):
        super().__init__()

    def generate_questions(self, project_data: Dict[str, Any], question_types: List[str]) -> List[Dict[str, Any]]:
        """根据项目信息和问题类型生成问答数据
        
        Args:
            project_data: 项目信息，包含name, description, technologies, responsibilities, achievements等字段
            question_types: 问题类型列表，可包含basic, technical, design, challenge等
            
        Returns:
            问答数据列表，每项包含question, answer, type, score_criteria字段
        """
        # 调用增强版生成器生成问答数据
        enhanced_qa_data = super().generate_questions(project_data, question_types)
        
        # 转换为原有格式
        qa_data = []
        for item in enhanced_qa_data:
            # 合并主问题和追问
            questions = [item['main_question']] + item['follow_up_questions']
            answers = [item['answers']['main']] + item['answers']['follow_up']
            
            # 提取评分标准
            score_criteria = []
            for dimension in item['scoring_dimensions'].values():
                score_criteria.extend(dimension['criteria'])
            
            # 添加到结果列表
            for q, a in zip(questions, answers):
                qa_data.append({
                    'question': q,
                    'answer': a,
                    'type': item['type'],
                    'score_criteria': score_criteria
                })

        # print(qa_data)

        return qa_data
import os
import json
import dotenv
import pytest
import requests
import socket
from multiprocessing import Process
from backend.test.app import app


def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def run_flask_app():
    """运行Flask应用的函数"""
    app.run(host="127.0.0.1", port=5088)

@pytest.fixture(scope="module")
def flask_app():
    # 检查端口是否已被占用
    if not is_port_in_use(5088):
        # 启动Flask应用
        server = Process(target=run_flask_app)
        server.start()
        yield
        server.terminate()
        server.join()
    else:
        # 端口已被占用，假设已有服务器在运行
        print("端口5088已被占用，使用现有服务器")
        yield

def test_project_qa(flask_app):
    # 测试文件路径
    test_file_path = os.path.join(os.path.dirname(__file__), "test.docx")
    
    # 确保测试文件存在
    assert os.path.exists(test_file_path), "测试文件不存在"
    
    # 首先上传简历获取项目信息
    with open(test_file_path, "rb") as f:
        files = {"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        response = requests.post("http://127.0.0.1:5088/api/interviews/upload", files=files)
        assert response.status_code == 200, f"简历上传失败: {response.text}"
        resume_data = response.json()
    
    # 确保解析出了项目信息
    assert "projects" in resume_data, "简历中未包含项目信息"
    assert len(resume_data["projects"]) > 0, "未解析出任何项目"
    
    # 针对每个项目生成问答
    for project in resume_data["projects"]:
        # 准备项目数据
        project_data = {
            "project": project,
            "question_types": ["basic", "technical", "design", "challenge"]
        }
        
        # 调用问答生成接口
        response = requests.post(
            "http://127.0.0.1:5088/api/interviews/generate_questions",
            json=project_data
        )
        
        # 验证响应状态
        assert response.status_code == 200, f"问题生成失败: {response.text}"
        
        # 解析问答数据
        qa_data = response.json()
        
        # 验证问答数据结构
        assert isinstance(qa_data, list), "返回的问答数据不是列表类型"
        assert len(qa_data) > 0, "未生成任何问题"
        
        # 验证每个问答的结构和内容
        for qa_item in qa_data:
            # 验证基本字段
            assert "question" in qa_item, "问答项缺少question字段"
            assert "answer" in qa_item, "问答项缺少answer字段"
            assert "type" in qa_item, "问答项缺少type字段"
            assert "score_criteria" in qa_item, "问答项缺少score_criteria字段"
            
            # 验证字段类型
            assert isinstance(qa_item["question"], str), "question字段不是字符串类型"
            assert isinstance(qa_item["answer"], str), "answer字段不是字符串类型"
            assert isinstance(qa_item["type"], str), "type字段不是字符串类型"
            assert isinstance(qa_item["score_criteria"], list), "score_criteria字段不是列表类型"
            
            # 验证问题类型
            assert qa_item["type"] in ["basic", "technical", "design", "challenge"], f"未知的问题类型: {qa_item['type']}"
            
            # 验证评分标准
            for criteria in qa_item["score_criteria"]:
                assert isinstance(criteria, dict), "评分标准项不是字典类型"
                assert "score" in criteria, "评分标准缺少score字段"
                assert "description" in criteria, "评分标准缺少description字段"
                assert isinstance(criteria["score"], (int, float)), "score字段不是数值类型"
                assert isinstance(criteria["description"], str), "description字段不是字符串类型"

if __name__ == "__main__":
    pytest.main([__file__])
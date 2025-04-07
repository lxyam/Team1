import os
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

        print(qa_data)
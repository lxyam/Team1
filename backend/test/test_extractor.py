import os
import json
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

def test_resume_extraction(flask_app):
    # 测试文件路径
    test_file_path = os.path.join(os.path.dirname(__file__), "test.docx")
    
    # 确保测试文件存在
    assert os.path.exists(test_file_path), "测试文件不存在"
    
    # 准备上传文件
    with open(test_file_path, "rb") as f:
        files = {"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        
        # 发送POST请求
        response = requests.post("http://127.0.0.1:5088/api/interviews/upload", files=files)
        
        # 验证响应状态码
        assert response.status_code == 200, f"请求失败: {response.text}"
        
        # 解析响应数据
        data = response.json()
        
        # 验证返回的数据结构
        assert isinstance(data, dict), "返回数据不是字典类型"
        assert "education" in data, "缺少education字段"
        assert "projects" in data, "缺少projects字段"
        assert "work_experience" in data, "缺少work_experience字段"
        assert "skills" in data, "缺少skills字段"
        assert "advantages" in data, "缺少advantages字段"
        
        # 验证projects字段的数据结构
        for project in data["projects"]:
            assert "name" in project, "项目缺少name字段"
            assert "description" in project, "项目缺少description字段"
            assert "technologies" in project, "项目缺少technologies字段"
            assert "responsibilities" in project, "项目缺少responsibilities字段"
            assert "achievements" in project, "项目缺少achievements字段"
            
            # 验证字段类型
            assert isinstance(project["name"], str), "项目name字段不是字符串类型"
            assert isinstance(project["description"], str), "项目description字段不是字符串类型"
            assert isinstance(project["technologies"], list), "项目technologies字段不是列表类型"
            assert isinstance(project["responsibilities"], list), "项目responsibilities字段不是列表类型"
            assert isinstance(project["achievements"], list), "项目achievements字段不是列表类型"

if __name__ == "__main__":
    pytest.main([__file__])
import os
import sys
import json
import requests
import socket
import time
from multiprocessing import Process
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def run_flask_app():
    """运行 Flask 应用"""
    app.run(host="127.0.0.1", port=5088)

def test_resume_extraction():
    test_file_path = os.path.join(os.path.dirname(__file__), "data/test_problematic_resume.docx")
    assert os.path.exists(test_file_path), "测试文件不存在"

    with open(test_file_path, "rb") as f:
        files = {"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        response = requests.post("http://127.0.0.1:5088/api/interviews/upload", files=files)
        assert response.status_code == 200, f"请求失败: {response.text}"

        data = response.json()
        print("接口返回的数据：", json.dumps(data, indent=2, ensure_ascii=False))

        # 构造保存路径
        output_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(output_dir, exist_ok=True)  # 如果 data 目录不存在，自动创建

        output_file = os.path.join(output_dir, "test_extractor_problematic.json")

        # 保存为 JSON 文件
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ 数据已保存到 {output_file}")

        assert isinstance(data, dict), "返回数据不是字典类型"
        assert "education" in data, "缺少education字段"
        assert "projects" in data, "缺少projects字段"
        assert "work_experience" in data, "缺少work_experience字段"
        assert "skills" in data, "缺少skills字段"
        assert "advantages" in data, "缺少advantages字段"

        for project in data["projects"]:
            assert "name" in project, "项目缺少name字段"
            assert "description" in project, "项目缺少description字段"
            assert "technologies" in project, "项目缺少technologies字段"
            assert "responsibilities" in project, "项目缺少responsibilities字段"
            assert "achievements" in project, "项目缺少achievements字段"

            assert isinstance(project["name"], str)
            assert isinstance(project["description"], str)
            assert isinstance(project["technologies"], list)
            assert isinstance(project["responsibilities"], list)
            assert isinstance(project["achievements"], list)

if __name__ == "__main__":
    server = None
    started_here = False

    # 启动服务（如果端口没被占用）
    if not is_port_in_use(5088):
        print("🔧 启动 Flask 应用...")
        server = Process(target=run_flask_app)
        server.start()
        started_here = True
        time.sleep(1.5)  # 等 Flask 启动

    try:
        test_resume_extraction()
        print("✅ 测试通过")
    except AssertionError as e:
        print("❌ 测试失败:", e)
    finally:
        if server and started_here:
            print("🛑 关闭 Flask 应用")
            server.terminate()
            server.join()

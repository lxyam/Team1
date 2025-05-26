import requests
import json

# 测试后端接口
def test_backend():
    # 测试简历上传接口
    print("测试后端接口...")
    
    # 检查服务是否运行
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ 后端服务正在运行")
        else:
            print("❌ 后端服务未正常运行")
            return
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return
    
    # 测试上传接口（使用测试文件）
    test_file_path = "backend/test/data/test.docx"
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = requests.post("http://localhost:8000/api/resume/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 简历上传接口正常")
                print("返回数据结构:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"❌ 简历上传失败: {response.status_code}")
                print(response.text)
                
    except FileNotFoundError:
        print(f"❌ 测试文件不存在: {test_file_path}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_backend() 
import os
import sys
import json
import requests
import socket
import time
import logging
from multiprocessing import Process
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app import app

# 设置日志级别为WARNING，减少INFO输出
logging.basicConfig(level=logging.WARNING)

# 抑制特定模块的日志
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('openai._base_client').setLevel(logging.WARNING)
logging.getLogger('backend.qa_engine').setLevel(logging.WARNING)

# 确保环境变量加载
load_dotenv()

def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def run_flask_app():
    """运行Flask应用的函数"""
    print("启动Flask应用，端口:5088...")
    app.run(host="127.0.0.1", port=5088, debug=False)  # 设置debug=False避免重新加载

def start_server():
    """启动服务器"""
    if not is_port_in_use(5088):
        print("端口5088未被占用，启动新服务器...")
        server = Process(target=run_flask_app)
        server.daemon = True  # 设置为守护进程，确保主进程结束时子进程也会结束
        server.start()
        
        # 等待服务器启动，最多等待10秒
        start_time = time.time()
        while time.time() - start_time < 30:
            if is_port_in_use(5088):
                print("服务器已成功启动")
                return server
            print("等待服务器启动...")
            time.sleep(0.5)
            
        print("警告：服务器可能未成功启动，请检查后端配置")
        return server
    else:
        print("端口5088已被占用，使用现有服务器")
        return None

def stop_server(server):
    """停止服务器"""
    if server:
        server.terminate()
        server.join()

def try_api_connection(max_retries=3):
    """测试API连接是否正常，最多尝试指定次数"""
    print("测试API连接...")
    
    # 首先确认端口是否开放
    if not is_port_in_use(5088):
        print("端口5088未开放，API服务器未启动")
        return False
        
    # 先测试直接的Flask路由
    for attempt in range(1, max_retries + 1):
        try:
            print(f"第{attempt}次尝试连接Flask应用...")
            direct_response = requests.get(
                "http://127.0.0.1:5088/test",
                timeout=10
            )
            if direct_response.status_code == 200:
                print(f"Flask应用连接成功: {direct_response.json().get('message', '无消息')}")
                break
            else:
                print(f"Flask应用返回错误状态码: {direct_response.status_code}")
                if attempt == max_retries:
                    print("Flask应用连接测试失败，可能存在基本配置问题")
                    return False
        except Exception as e:
            print(f"Flask应用连接异常: {str(e)}")
            if attempt == max_retries:
                print("Flask应用连接测试失败，请检查服务器是否正常运行")
                return False
        
        if attempt < max_retries:
            print(f"等待0.5秒后重试...")
            time.sleep(0.5)
            
    # 然后测试API路由
    for attempt in range(1, max_retries + 1):
        try:
            print(f"第{attempt}次尝试连接API...")
            test_response = requests.get(
                "http://127.0.0.1:5088/api/interview/test",
                timeout=2  # 减少超时时间
            )
            if test_response.status_code == 200:
                print(f"API连接成功: {test_response.json().get('message', '无消息')}")
                return True
            else:
                print(f"API返回错误状态码: {test_response.status_code}")
        except requests.exceptions.Timeout:
            print(f"第{attempt}次尝试API连接超时...")
        except requests.exceptions.ConnectionError:
            print(f"第{attempt}次尝试API连接错误，服务器可能未启动...")
        except Exception as e:
            print(f"第{attempt}次尝试API测试异常: {str(e)}")
        
        # 如果不是最后一次尝试，等待一段时间
        if attempt < max_retries:
            print(f"等待0.5秒后重试...")
            time.sleep(0.5)  # 减少等待时间
    
    print("API连接测试失败，请检查服务器是否正常运行")
    return False

def main():
    """测试多轮面试功能"""
    # 打印环境变量信息一次
    print("环境变量:")
    print(f"OPENAI_API_KEY: {'已设置' if os.getenv('OPENAI_API_KEY') else '未设置'}")
    print(f"OPENAI_API_BASE: {os.getenv('OPENAI_API_BASE')}")
    print(f"OPENAI_MODEL: {os.getenv('OPENAI_MODEL', 'deepseek-chat')}")
    
    # 启动服务器
    server = start_server()
    
    try:
        # 从JSON文件加载项目数据
        test_file_path = os.path.join(os.path.dirname(__file__), "data/test_extractor.json")
        with open(test_file_path, 'r', encoding='utf8') as fp:
            data = json.load(fp)
        
        # 获取第一个项目数据
        project_data = data["projects"][0]
        
        print("使用项目数据:", json.dumps(project_data, ensure_ascii=False, indent=2))

        # 测试API连接，如果失败则退出
        if not try_api_connection(max_retries=3):
            print("由于API连接失败，无法继续执行面试过程")
            return

        # 1. 开始面试
        try:
            response = requests.post(
                "http://127.0.0.1:5088/api/interview/start",
                json=project_data,
                timeout=60  # 设置60秒超时
            )
            if response.status_code == 200:
                session_data = response.json()
                session_id = session_data["session_id"]
                
                # 2. 进行多轮对话
                print("\n=== 开始面试 ===")
                print(f"\n=== 第{1}轮对话 ===")
                print(f"面试官: {session_data['question']}")
                user_answer = input("请输入你的回答: ")
                print(f"参考答案: {session_data['candidate_answer']}")
                max_rounds = 5
                for round_num in range(2, max_rounds + 1):
                    print(f"\n=== 第{round_num}轮对话 ===")
                    # 获取用户输入
                    # user_answer = input("请输入你的回答: ")
                    # 继续面试
                    try:
                        response = requests.post(
                            "http://127.0.0.1:5088/api/interview/continue",
                            json={
                                "session_id": session_id,
                                "answer": user_answer
                            },
                            timeout=60  # 设置60秒超时
                        )
                        if response.status_code == 200:
                            result = response.json()
                            if result["status"] == "completed":
                                print("\n=== 面试结束 ===")
                                print("评估结果:")
                                print(json.dumps(result["evaluation"], ensure_ascii=False, indent=2))
                                break
                            else:
                                print(f"面试官: {result['question']}")
                                user_answer = input("请输入你的回答: ")
                                print(f"参考答案: {result['candidate_answer']}")
                        else:
                            print(f"继续面试失败: {response.text}")
                            break
                    except requests.exceptions.RequestException as e:
                        print(f"请求超时或错误: {str(e)}")
                        print("请检查网络连接或API服务可用性")
                        break

                # 3. 获取面试状态
                try:
                    response = requests.get(
                        f"http://127.0.0.1:5088/api/interview/{session_id}/status",
                        timeout=10
                    )
                    if response.status_code == 200:
                        status = response.json()
                        print(f"\n面试状态: 已完成{status['rounds_completed']}轮，共{status['total_rounds']}轮")
                    else:
                        print(f"获取面试状态失败: {response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"获取状态请求失败: {str(e)}")

                # 4. 结束面试
                try:
                    response = requests.delete(
                        f"http://127.0.0.1:5088/api/interview/{session_id}",
                        timeout=10
                    )
                    if response.status_code == 200:
                        print("\n面试已结束")
                    else:
                        print(f"结束面试失败: {response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"结束面试请求失败: {str(e)}")
            else:
                print(f"开始面试失败: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"请求超时或错误: {str(e)}")
            print("请检查网络连接或API服务可用性")
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
    finally:
        # 停止服务器
        stop_server(server)

if __name__ == "__main__":
    main()
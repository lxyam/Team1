import os
from dotenv import load_dotenv
import openai
import json

# 加载环境变量
load_dotenv()

def clean_json_content(content):
    """清理可能包含markdown格式的JSON内容"""
    content = content.strip()
    if content.startswith('```') and content.endswith('```'):
        content = content.split('\n', 1)[1].rsplit('\n', 1)[0]
    if content.startswith('```json'):
        content = content.split('\n', 1)[1]
    return content

def test_api():
    # 获取环境变量
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE')
    model = os.getenv('OPENAI_MODEL', 'deepseek-chat')
    
    print(f"API Key: {api_key[:8]}...")  # 只打印前8位
    print(f"API Base: {api_base}")
    print(f"Model: {model}")
    
    # 配置 OpenAI
    openai.api_key = api_key
    openai.api_base = api_base
    
    # 测试文本
    test_text = """
    教育背景：
    北京大学，计算机科学与技术，本科，2020年毕业
    
    工作经历：
    字节跳动，后端开发工程师，2020-2022
    负责抖音后端服务开发
    
    技能特长：
    Python, Java, Go, Docker, Kubernetes
    
    项目经验：
    抖音直播服务优化，提升系统性能30%
    """
    
    try:
        print("\n正在调用 API...")
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """你是一个简历分析助手。请分析文本并直接返回JSON格式数据（不要添加markdown标记）：
                    {
                        "education": [{"school": "", "degree": "", "major": "", "graduation_year": ""}],
                        "work_experience": [{"company": "", "position": "", "duration": "", "responsibilities": []}],
                        "skills": [],
                        "projects": [{"name": "", "description": "", "technologies": [], "responsibilities": [], "achievements": []}],
                        "advantages": []
                    }
                    注意：直接返回JSON，不要添加任何markdown标记。"""
                },
                {
                    "role": "user",
                    "content": test_text
                }
            ],
            temperature=0.7,
            request_timeout=60
        )
        
        print("\nAPI 调用成功！")
        print("\n原始响应：")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        content = response.choices[0].message.content
        print("\n原始内容：")
        print(content)
        
        # 清理并解析 JSON
        cleaned_content = clean_json_content(content)
        print("\n清理后的内容：")
        print(cleaned_content)
        
        try:
            json_content = json.loads(cleaned_content)
            print("\n解析后的 JSON：")
            print(json.dumps(json_content, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print("\nJSON 解析失败：", str(e))
            
    except Exception as e:
        print("\n调用失败：", str(e))
        print("错误类型：", type(e).__name__)

if __name__ == "__main__":
    test_api() 
from dotenv import load_dotenv
from openai import OpenAI
import os

from backend.parser.extractor import extract_resume, check_resume_issues
from backend.qa_engine.projects import projects_main
from backend.qa_engine.advantages import advantages_main
from backend.code.code_question_generotor import generate_interview_code_question
from backend.evaluate.report import evaluation

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-06a1fc23f04940cf93e06e4b39e1f949")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.deepseek.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-chat")

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE,
    default_headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
)

# 只保留导入、client初始化和函数暴露，不要有任何主流程代码


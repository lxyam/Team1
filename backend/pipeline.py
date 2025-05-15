from dotenv import load_dotenv
from openai import OpenAI

from backend.parser.extractor import extract_resume, check_resume_issues
from backend.qa_engine.projects import projects_main
from backend.qa_engine.advantages import advantages_main
from backend.code.code_question_generotor import generate_interview_code_question
from backend.evaluate.report import evaluation
load_dotenv()

OPENAI_API_KEY = "sk-06a1fc23f04940cf93e06e4b39e1f949"
OPENAI_API_BASE = "https://api.deepseek.com"
OPENAI_MODEL = "deepseek-chat"

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE
)

# 简历文件接受前端输入后存到test/data/test.docx
file_path = "test/data/test.docx"
resume = None
try:
    resume = extract_resume(file_path)
except Exception as e:
    print('提取失败: 简历信息不足，存在缺少技术栈、成果描述或技能列表等问题，请补充后重新上传')

if resume:
    if len(check_resume_issues(resume)) != 0:
        print('简历内容缺少需要补充')
    else:
        # 项目问答
        projects = projects_main(resume, client)
        print(projects)
        # 返回格式：{'project': [{'question': '', 'answer': ''}], ...}
        # 个人优势
        advantages = advantages_main(resume, client)
        print(advantages)
        # 返回格式：{'question': '', 'answer': '', 'reason': ''}
        # 编程题
        code = generate_interview_code_question(resume, client)
        print(code)
        # 返回格式： ('', '') (question, answer)的元组
        ans = {} # todo: ans回答数据从前端传入
        # 评估
        final_report = evaluation(client, projects, advantages, code, ans)
        print(final_report)


from backend.parser.extractor import extract_resume, check_resume_issues
from backend.qa_engine.projects import projects_main
from backend.qa_engine.advantages import advantages_main
from backend.code.code_question_generotor import generate_interview_code_question

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
        projects = projects_main(resume)
        print(projects)
        # 个人优势
        advantages = advantages_main(resume)
        print(advantages)
        # 编程题
        code = generate_interview_code_question(resume)
        print(code)
        ans = '' # todo: ans回答数据从前端传入



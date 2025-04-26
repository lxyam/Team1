from extractor import extract_resume 

# 示例调用
file_path = "backend/test/data/test.docx"   
result = extract_resume(file_path)
# 示例输出
print(result)
# {'education': [{'school': '北京大学', 'degree': '本科', 'major': '计算机科学与技术', 'graduation_year': '2018'}, {'school': '清华大学', 'degree': '硕士', 'major': '计算机科学与技术', 'graduation_year': '2021'}], 'projects': [{'name': '智能简历分析系统', 'description': '基于NLP的简历自动解析平台', 'technologies': ['Python', 'FastAPI', 'PostgreSQL', 'OpenAI API', 'BERT', 'LSTM', 'TensorFlow', 'PyTorch'], 'responsibilities': ['负责简历内容的解析与分类，设计并实现了基于BERT的文本分类模型'], 'achievements': ['系统上线后，节省了80%的人 工筛选时间，并提高了筛选准确率']}, {'name': '个性化推荐系统', 'description': '基于深度学习的个性化推荐平台', 'technologies': ['Python', 'Flask', 'TensorFlow', 'Keras', 'Apache Spark', 'Collaborative Filtering', 'Matrix Factorization', 'XGBoost'], 'responsibilities': ['负责推荐算法的设计与优化，采用矩阵分解和协同过滤结合深度学习模型', '使用Keras训练神经网络进行内容推荐，并使用XGBoost优化模型'], 'achievements': ['推荐系统上线后，用户活跃度提高了30%，点击率提升了18%']}], 'work_experience': [{'company': '字节跳动', 'position': '后端开发工程师', 'duration': '2019年-2021年', 'responsibilities': ['负责公司内部API系统的开发、优化和维护，提升系统性能和可扩展性'], 'achievements': ['主导重构任务调度模块，系统响应时间减少30%', '设计并实现跨平台的文件上传系统，支持高并发请求，性能提高40%', '使用消息队列（Kafka）实现异步任务处理，减少了30%的API响应时间', '提升系统的稳定性和故障恢复能力，确保了99.99%的系统可用性']}, {'company': '腾讯', 'position': '机器学习工程师', 'duration': '2021年-2023年', 'responsibilities': ['负责推荐系统、搜索引擎以及个性化推荐算法的研发', '使用深度学习模型优化推荐算法和搜索排名'], 'achievements': ['基于BERT和Transformer的搜索排序优化，系统准确率提升20%', '采用协同过滤与矩阵分解结合深度学习模型，提升了用户点击率30%', '设计并实现了用户行为分析平台，使用Spark和Kafka处理大规模数据', '参与开发机器学习平台，支持多 种机器学习框架（TensorFlow、PyTorch）']}, {'company': '阿里巴巴', 'position': '数据科学家', 'duration': '2023年至今', 'responsibilities': ['负责大数据分析与机器学习模型的应用', '专注于数据挖掘、文本分析、推荐系统和个性化广告'], 'achievements': ['使用XGBoost和LightGBM 进行用户画像分析，广告点击率提升15%', '在大数据平台上开发实时推荐系统，月活跃用户提升了25%', '通过强化学习优化个性化广告投放策略，实现广告投放ROI的提高']}], 'skills': ['Python', 'JavaScript', 'C++', 'Java', 'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Cassandra', 'TensorFlow', 'PyTorch', 'Keras', 'BERT', 'LSTM', '协同过滤', '矩阵分解', 'XGBoost', 'LightGBM', '强化学习', 'Pandas', 'NumPy', 'Apache Spark', 'Hadoop', 'Kafka', 'Flink', 'Elasticsearch', 'FastAPI', 'Flask', 'Django', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'Git', 'Jenkins', 'GitLab CI', 'RESTful API', '数据可视化', '数据挖掘', '自动化测试'], 'advantages': ['精通机器学习和深度学习算法，尤其在自然语言处理 （NLP）和推荐系统领域有丰富经验', '擅长数据挖掘与大数据分析，能够处理和分析大规模数据集，并提取有价值的信息', '强大的问题解决能力和算 法优化能力，能够迅速定位和解决系统性能瓶颈', '具备良好的团队合作和项目管理能力，能够有效推动跨部门的技术合作与交流', '对技术有深厚的热情，能够自我驱动并持续学习新技术']}

# 示例调用
file_path2 = "backend/test/data/test_problematic_resume.docx"   
result2 = extract_resume(file_path2)
# [❌] 提取失败: 简历信息不足，存在以下问题：项目《智能简历分析系统》缺少技术栈; 项目《智能简历分析系统》缺少成果描述; 项目《个性化推荐 系统》缺少技术栈; 项目《个性化推荐系统》缺少成果描述; 缺少技能列表
# 示例输出
print(result2)
# {}



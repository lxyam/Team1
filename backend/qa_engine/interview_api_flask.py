from typing import Dict, Any
from flask import Blueprint, request, jsonify
from .item import InterviewSession
import logging
import traceback
import os

# 设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)  # 将日志级别设置为WARNING，减少INFO日志输出

flask_router = Blueprint('interview', __name__)
interview_sessions = {}  # 存储面试会话

# 添加测试路由以验证API是否正常工作
@flask_router.route("/interview/test", methods=['GET'])
def test_api():
    """测试API是否正常工作"""
    try:
        logger.info("测试API路由被访问")
        # 简单返回状态，不做任何复杂操作
        return jsonify({"message": "API正常工作", "status": "success"}), 200
    except Exception as e:
        logger.error(f"测试API异常: {str(e)}")
        return jsonify({"error": "API测试失败", "details": str(e)}), 500

@flask_router.route("/interview/start", methods=['POST'])
def start_interview():
    """开始一个新的面试会话"""
    try:
        logger.info("开始新面试会话")
        
        # 简单验证请求
        if not request.is_json:
            return jsonify({"error": "请求必须是JSON格式"}), 400
            
        # 获取JSON数据
        project_data = request.json
        if not project_data:
            return jsonify({"error": "项目数据为空"}), 400
            
        logger.info(f"接收到项目数据: {project_data}")
        
        # 检查必要的项目数据字段
        required_fields = ["name", "description", "technologies"]
        missing_fields = [field for field in required_fields if field not in project_data]
        if missing_fields:
            return jsonify({"error": f"缺少必要的项目数据字段: {', '.join(missing_fields)}"}), 400
        
        # 简化会话创建过程
        try:
            session = InterviewSession(project_data)
            session_id = str(len(interview_sessions) + 1)  # 简单的会话ID生成
            interview_sessions[session_id] = session
            
            # 生成第一个问题
            result = session.start_interview()
            
            logger.info(f"生成会话ID: {session_id}")
            return jsonify({
                "session_id": session_id,
                "question": result["question"],
                "candidate_answer": result["candidate_answer"]
            })
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"会话创建或问题生成失败: {str(e)}\n{error_traceback}")
            
            # 提供更有用的错误信息
            error_message = str(e)
            if "api_key" in error_message.lower():
                error_message = "API密钥无效或未设置正确"
            elif "connection" in error_message.lower():
                error_message = "连接到OpenAI API失败，请检查网络或API基础URL"
                
            return jsonify({
                "error": "启动面试失败",
                "reason": error_message,
                "details": str(e)
            }), 500
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"开始面试失败: {str(e)}\n{error_traceback}")
        return jsonify({"error": str(e)}), 500

@flask_router.route("/interview/continue", methods=['POST'])
def continue_interview():
    """继续面试会话"""
    try:
        data = request.json
        session_id = data.get("session_id")
        user_answer = data.get("answer")
        
        session = interview_sessions.get(session_id)
        if not session:
            return jsonify({"error": "面试会话不存在"}), 404
        
        result = session.continue_interview(user_answer)
        if result is None:
            # 面试结束，返回评估结果
            evaluation = session.evaluate_answers()
            # 清理会话
            del interview_sessions[session_id]
            return jsonify({
                "status": "completed",
                "evaluation": evaluation
            })
        
        return jsonify({
            "status": "continue",
            "question": result["question"],
            "candidate_answer": result["candidate_answer"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@flask_router.route("/interview/<session_id>/status", methods=['GET'])
def get_interview_status(session_id):
    """获取面试会话状态"""
    try:
        session = interview_sessions.get(session_id)
        if not session:
            return jsonify({"error": "面试会话不存在"}), 404
        
        return jsonify({
            "rounds_completed": len(session.conversation_history) // 2,  # 每轮包含一个问题和一个回答
            "total_rounds": 5,
            "conversation_history": session.conversation_history
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@flask_router.route("/interview/<session_id>", methods=['DELETE'])
def end_interview(session_id):
    """结束面试会话"""
    try:
        if session_id in interview_sessions:
            session = interview_sessions[session_id]
            evaluation = session.evaluate_answers()
            del interview_sessions[session_id]
            return jsonify({
                "status": "success",
                "message": "面试会话已结束",
                "evaluation": evaluation
            })
        return jsonify({"error": "面试会话不存在"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
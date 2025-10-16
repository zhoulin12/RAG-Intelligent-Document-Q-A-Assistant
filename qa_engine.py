from typing import List, Dict, Any, Optional
from config import system_config
from zhipu_service import zhipu_service
from vector_db import VectorDBManager
from logger import get_logger

logger = get_logger(__name__)

class QAEngine:
    """问答引擎 - 负责生成答案"""
    
    def __init__(self, vector_db_manager: VectorDBManager):
        self.vector_db = vector_db_manager
        self.config = system_config
    
    def answer_question(self, question: str, top_k: int = None) -> Dict[str, Any]:
        """回答问题"""
        try:
            # 检索相关文档
            search_results = self.vector_db.search(question, top_k)
            
            if not search_results:
                return {
                    "success": True,
                    "answer": "抱歉，我没有找到相关的信息来回答这个问题。",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # 构建上下文
            context = self._build_context(search_results)
            
            # 生成答案
            answer_data = self._generate_answer(question, context)
            
            # 添加来源信息
            answer_data["sources"] = search_results
            answer_data["confidence"] = max([result["similarity"] for result in search_results])
            
            return answer_data
            
        except Exception as e:
            error_msg = f"生成答案失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "answer": f"生成答案时出现错误: {error_msg}",
                "sources": [],
                "confidence": 0.0
            }
    
    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """构建上下文"""
        context_parts = []
        
        for i, result in enumerate(search_results):
            source_info = f"来源 {i+1}: {result['metadata'].get('source', '未知文档')}"
            context_parts.append(f"{source_info}\n{result['content']}")
        
        return "\n\n".join(context_parts)
    
    def _generate_answer(self, question: str, context: str) -> Dict[str, Any]:
        """生成答案"""
        system_prompt = """你是一个专业的问答助手，请基于提供的上下文信息回答用户的问题。
请遵循以下原则：
1. 只基于提供的上下文信息回答问题
2. 如果上下文信息不足以回答问题，请说明你不知道
3. 回答要准确、简洁、有条理
4. 可以适当引用上下文中的具体内容
5. 回答使用中文"""
        
        user_prompt = f"""上下文信息：
{context}

问题：{question}

请基于上述上下文信息回答问题。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 调用智普AI生成答案
        response = zhipu_service.chat_completion(messages)
        
        if response["success"]:
            return {
                "success": True,
                "answer": response["content"],
                "usage": response.get("usage", {}),
                "model": response.get("model", "")
            }
        else:
            return {
                "success": False,
                "answer": response.get("content", "生成答案失败"),
                "error": response.get("error", "")
            }
    
    def batch_answer_questions(self, questions: List[str]) -> List[Dict[str, Any]]:
        """批量回答问题"""
        results = []
        for question in questions:
            result = self.answer_question(question)
            results.append({
                "question": question,
                "success": result["success"],
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "confidence": result.get("confidence", 0.0)
            })
        return results
    
    def get_source_summary(self, source_id: str) -> Dict[str, Any]:
        """获取来源摘要"""
        try:
            # 根据source_id检索相关文档块
            filter_dict = {"source": source_id}
            search_results = self.vector_db.search("", filter_dict=filter_dict)
            
            if not search_results:
                return {
                    "success": False,
                    "message": f"未找到来源: {source_id}"
                }
            
            # 构建摘要
            summary_prompt = f"""请为以下文档内容生成一个简洁的摘要：

{chr(10).join([result["content"] for result in search_results])}"""
            
            messages = [
                {"role": "system", "content": "你是一个专业的文档摘要助手，请生成简洁、准确的文档摘要。"},
                {"role": "user", "content": summary_prompt}
            ]
            
            response = zhipu_service.chat_completion(messages)
            
            if response["success"]:
                return {
                    "success": True,
                    "summary": response["content"],
                    "chunks_count": len(search_results)
                }
            else:
                return {
                    "success": False,
                    "message": "生成摘要失败"
                }
                
        except Exception as e:
            error_msg = f"获取摘要失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg
            }
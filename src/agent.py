"""
LangChain Agent 核心模組
負責協調所有工具執行並處理訊息
"""
import logging
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

from .config import settings
from .prompts import PromptManager
from .database import SyncDatabaseManager as DatabaseManager
from .schemas import MessageRequest, OrganizeResponse, ToneProfile, AgentExecutionLog, ToolResult
from .constants import ERROR_MESSAGES, PERFORMANCE_THRESHOLDS
from .toolbox import get_all_tools

logger = logging.getLogger(__name__)


class MessageAgent:
    """訊息處理 Agent"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.prompt_manager = PromptManager(self.db)
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens
        )
        self.tools = get_all_tools()
        logger.info("MessageAgent 初始化完成")
    
    async def process_message(self, request: MessageRequest) -> OrganizeResponse:
        """
        處理訊息的主要入口點
        
        Args:
            request: 訊息處理請求
            
        Returns:
            處理結果
        """
        start_time = time.time()
        execution_log = {
            'user_id': request.sender_id,
            'message_text': request.text,
            'prompt_used': '',
            'tool_results': [],
            'final_response': {},
            'total_execution_time': 0,
            'token_usage': {},
            'timestamp': datetime.now()
        }
        
        try:
            logger.info(f"開始處理用戶 {request.sender_id} 的訊息，長度: {len(request.text)}")
            
            # 1. 載入並渲染 System Prompt
            prompt_template = self.prompt_manager.get_user_prompt(request.sender_id)
            system_prompt = self.prompt_manager.render_prompt(prompt_template, request.tone_profile)
            execution_log['prompt_used'] = system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt
            
            logger.debug(f"使用 System Prompt 長度: {len(system_prompt)}")
            
            # 2. 建立 Agent
            agent = self._create_agent(system_prompt)
            
            # 3. 執行處理
            result = await self._execute_agent(agent, request.text, execution_log)
            
            # 4. 計算執行時間
            execution_time = time.time() - start_time
            execution_log['total_execution_time'] = execution_time
            execution_log['final_response'] = result.dict()
            
            # 5. 記錄成功日誌
            logger.info(f"訊息處理完成，用戶: {request.sender_id}, 耗時: {execution_time:.2f}s, "
                       f"分類: {result.category}, 優先級: {result.priority}")
            
            # 6. 檢查效能警告
            self._check_performance_warnings(execution_time, execution_log['tool_results'])
            
            # 7. 記錄到資料庫
            await self._log_execution(execution_log)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            execution_log['total_execution_time'] = execution_time
            
            logger.error(f"訊息處理失敗，用戶: {request.sender_id}, 耗時: {execution_time:.2f}s, 錯誤: {str(e)}")
            
            # 記錄失敗日誌
            execution_log['final_response'] = {'error': str(e)}
            await self._log_execution(execution_log)
            
            raise
    
    def _create_agent(self, system_prompt: str) -> AgentExecutor:
        """建立 LangChain Agent"""
        try:
            # 建立 Prompt 模板
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=system_prompt),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])
            
            # 建立 Agent
            agent = create_openai_tools_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )
            
            # 建立 Agent Executor
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=settings.debug,
                max_iterations=5,
                early_stopping_method="generate"
            )
            
            return agent_executor
            
        except Exception as e:
            logger.error(f"建立 Agent 失敗: {e}")
            raise
    
    async def _execute_agent(self, agent: AgentExecutor, text: str, execution_log: Dict) -> OrganizeResponse:
        """執行 Agent 並記錄工具使用情況"""
        tool_results = []
        
        try:
            # 執行 Agent
            result = await agent.ainvoke({"input": text})
            
            # 解析結果
            if isinstance(result.get('output'), str):
                try:
                    parsed_result = json.loads(result['output'])
                except json.JSONDecodeError:
                    # 如果不是 JSON，嘗試提取關鍵資訊
                    parsed_result = self._parse_text_result(result['output'])
            else:
                parsed_result = result.get('output', {})
            
            # 記錄 Token 使用量（如果可用）
            if hasattr(result, 'llm_output') and result.llm_output:
                execution_log['token_usage'] = result.llm_output.get('token_usage', {})
            
            # 驗證結果格式
            response = self._validate_and_format_response(parsed_result)
            
            # 記錄工具執行結果
            execution_log['tool_results'] = tool_results
            
            return response
            
        except Exception as e:
            logger.error(f"Agent 執行失敗: {e}")
            # 回退機制：返回基本分類結果
            return self._create_fallback_response(text)
    
    def _validate_and_format_response(self, result: Dict[str, Any]) -> OrganizeResponse:
        """驗證並格式化回應"""
        try:
            # 確保必要欄位存在
            response_data = {
                'category': result.get('category', '朋友'),
                'tags': result.get('tags', []),
                'priority': int(result.get('priority', 3)),
                'should_archive': bool(result.get('should_archive', False)),
                'draft': result.get('draft', None)
            }
            
            # 驗證分類
            from .constants import CATEGORIES
            if response_data['category'] not in CATEGORIES:
                logger.warning(f"無效分類: {response_data['category']}，使用預設值")
                response_data['category'] = '朋友'
            
            # 驗證優先級
            if not (1 <= response_data['priority'] <= 5):
                logger.warning(f"無效優先級: {response_data['priority']}，使用預設值")
                response_data['priority'] = 3
            
            return OrganizeResponse(**response_data)
            
        except Exception as e:
            logger.error(f"結果驗證失敗: {e}")
            return self._create_fallback_response("")
    
    def _create_fallback_response(self, text: str) -> OrganizeResponse:
        """建立回退回應"""
        logger.warning("使用回退機制生成回應")
        return OrganizeResponse(
            category="朋友",
            tags=["需人工檢查"],
            priority=3,
            should_archive=False,
            draft=None
        )
    
    def _parse_text_result(self, text_result: str) -> Dict[str, Any]:
        """解析非 JSON 格式的文字結果"""
        # 簡單的文字解析邏輯
        result = {
            'category': '朋友',
            'tags': [],
            'priority': 3,
            'should_archive': False,
            'draft': None
        }
        
        # 嘗試提取分類
        text_lower = text_result.lower()
        if '工作' in text_result:
            result['category'] = '工作'
            result['priority'] = 2
        elif '家人' in text_result:
            result['category'] = '家人'
            result['priority'] = 1
        elif '廣告' in text_result:
            result['category'] = '廣告'
            result['priority'] = 5
            result['should_archive'] = True
        
        return result
    
    def _check_performance_warnings(self, execution_time: float, tool_results: list):
        """檢查效能警告"""
        # 檢查總執行時間
        if execution_time > PERFORMANCE_THRESHOLDS['MAX_TOTAL_EXECUTION_TIME']:
            logger.warning(f"執行時間超過閾值: {execution_time:.2f}s > {PERFORMANCE_THRESHOLDS['MAX_TOTAL_EXECUTION_TIME']}s")
        
        # 檢查個別工具執行時間
        for tool_result in tool_results:
            if tool_result.get('execution_time', 0) > PERFORMANCE_THRESHOLDS['MAX_TOOL_EXECUTION_TIME']:
                logger.warning(f"工具 {tool_result.get('tool_name')} 執行時間過長: {tool_result.get('execution_time'):.2f}s")
    
    async def _log_execution(self, execution_log: Dict[str, Any]):
        """記錄執行日誌到資料庫"""
        try:
            success = await self.db.log_agent_execution(execution_log)
            if not success:
                logger.error("執行日誌記錄失敗")
        except Exception as e:
            logger.error(f"記錄執行日誌時發生錯誤: {e}")
    
    async def get_user_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """獲取用戶統計資訊"""
        try:
            stats = await self.db.get_execution_stats(user_id, days)
            logger.info(f"獲取用戶 {user_id} 的 {days} 天統計")
            return stats
        except Exception as e:
            logger.error(f"獲取用戶統計失敗: {e}")
            return {}
    
    def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        try:
            # 檢查 LLM 連接
            test_response = self.llm.invoke("Hello")
            
            # 檢查工具載入
            tools_loaded = len(self.tools)
            
            return {
                "status": "healthy",
                "llm_connected": bool(test_response),
                "tools_loaded": tools_loaded,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"健康檢查失敗: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 
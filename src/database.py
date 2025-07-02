"""
資料庫管理模組
"""
import logging
import asyncpg
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class DatabaseManager:
    """資料庫管理器"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.pool = None
    
    async def init_pool(self):
        """初始化連接池"""
        try:
            self.pool = await asyncpg.create_pool(self.database_url)
            logger.info("資料庫連接池初始化成功")
        except Exception as e:
            logger.error(f"資料庫連接池初始化失敗: {e}")
            raise
    
    async def close_pool(self):
        """關閉連接池"""
        if self.pool:
            await self.pool.close()
            logger.info("資料庫連接池已關閉")
    
    async def create_tables(self):
        """建立資料表"""
        async with self.pool.acquire() as conn:
            # 建立用戶 Prompt 表
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_prompts (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(50) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    content TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT false,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(user_id, name)
                );
            """)
            
            # 建立唯一活躍 prompt 索引
            await conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_user_active_prompt 
                ON user_prompts (user_id) 
                WHERE is_active = true;
            """)
            
            # 建立聯絡人優先級表
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS contact_priorities (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(50) NOT NULL,
                    sender_id VARCHAR(50) NOT NULL,
                    priority_boost INTEGER DEFAULT 0,
                    is_starred BOOLEAN DEFAULT false,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(user_id, sender_id)
                );
            """)
            
            # 建立執行日誌表
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_execution_logs (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(50) NOT NULL,
                    message_text TEXT NOT NULL,
                    prompt_used TEXT NOT NULL,
                    tool_results JSONB NOT NULL,
                    final_response JSONB NOT NULL,
                    total_execution_time FLOAT NOT NULL,
                    token_usage JSONB NOT NULL,
                    timestamp TIMESTAMP DEFAULT NOW()
                );
            """)
            
            logger.info("資料表建立完成")
    
    async def get_active_prompt(self, user_id: str) -> Optional[Dict[str, Any]]:
        """獲取用戶活躍的 Prompt"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT id, name, content, created_at, updated_at
                FROM user_prompts 
                WHERE user_id = $1 AND is_active = true
            """, user_id)
            
            if result:
                return dict(result)
            return None
    
    async def save_user_prompt(self, user_id: str, name: str, content: str) -> bool:
        """儲存用戶 Prompt"""
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("""
                    INSERT INTO user_prompts (user_id, name, content, updated_at)
                    VALUES ($1, $2, $3, NOW())
                    ON CONFLICT (user_id, name) 
                    DO UPDATE SET content = $3, updated_at = NOW()
                """, user_id, name, content)
                return True
            except Exception as e:
                logger.error(f"儲存 Prompt 失敗: {e}")
                return False
    
    async def activate_prompt(self, user_id: str, prompt_id: int) -> bool:
        """啟用特定 Prompt"""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                try:
                    # 先停用所有 prompt
                    await conn.execute("""
                        UPDATE user_prompts 
                        SET is_active = false 
                        WHERE user_id = $1
                    """, user_id)
                    
                    # 啟用指定 prompt
                    result = await conn.execute("""
                        UPDATE user_prompts 
                        SET is_active = true, updated_at = NOW()
                        WHERE user_id = $1 AND id = $2
                    """, user_id, prompt_id)
                    
                    return result != "UPDATE 0"
                except Exception as e:
                    logger.error(f"啟用 Prompt 失敗: {e}")
                    return False
    
    async def get_user_prompts(self, user_id: str) -> List[Dict[str, Any]]:
        """獲取用戶所有 Prompt"""
        async with self.pool.acquire() as conn:
            results = await conn.fetch("""
                SELECT id, user_id, name, content, is_active, created_at, updated_at
                FROM user_prompts 
                WHERE user_id = $1
                ORDER BY created_at DESC
            """, user_id)
            
            return [dict(row) for row in results]
    
    async def delete_prompt(self, user_id: str, prompt_id: int) -> bool:
        """刪除 Prompt"""
        async with self.pool.acquire() as conn:
            try:
                result = await conn.execute("""
                    DELETE FROM user_prompts 
                    WHERE user_id = $1 AND id = $2
                """, user_id, prompt_id)
                
                return result != "DELETE 0"
            except Exception as e:
                logger.error(f"刪除 Prompt 失敗: {e}")
                return False
    
    async def get_contact_priority(self, user_id: str, sender_id: str) -> Dict[str, Any]:
        """獲取聯絡人優先級設定"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT priority_boost, is_starred
                FROM contact_priorities 
                WHERE user_id = $1 AND sender_id = $2
            """, user_id, sender_id)
            
            if result:
                return dict(result)
            return {"priority_boost": 0, "is_starred": False}
    
    async def set_contact_priority(self, user_id: str, sender_id: str, 
                                 priority_boost: int, is_starred: bool) -> bool:
        """設定聯絡人優先級"""
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("""
                    INSERT INTO contact_priorities (user_id, sender_id, priority_boost, is_starred, updated_at)
                    VALUES ($1, $2, $3, $4, NOW())
                    ON CONFLICT (user_id, sender_id) 
                    DO UPDATE SET 
                        priority_boost = $3, 
                        is_starred = $4, 
                        updated_at = NOW()
                """, user_id, sender_id, priority_boost, is_starred)
                return True
            except Exception as e:
                logger.error(f"設定聯絡人優先級失敗: {e}")
                return False
    
    async def log_agent_execution(self, log_data: Dict[str, Any]) -> bool:
        """記錄 Agent 執行日誌"""
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("""
                    INSERT INTO agent_execution_logs 
                    (user_id, message_text, prompt_used, tool_results, 
                     final_response, total_execution_time, token_usage)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                    log_data['user_id'],
                    log_data['message_text'],
                    log_data['prompt_used'],
                    log_data['tool_results'],
                    log_data['final_response'],
                    log_data['total_execution_time'],
                    log_data['token_usage']
                )
                return True
            except Exception as e:
                logger.error(f"記錄執行日誌失敗: {e}")
                return False
    
    async def get_execution_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """獲取執行統計"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_executions,
                    AVG(total_execution_time) as avg_execution_time,
                    SUM((token_usage->>'total_tokens')::int) as total_tokens
                FROM agent_execution_logs 
                WHERE user_id = $1 
                AND timestamp >= NOW() - INTERVAL '%s days'
            """, user_id, days)
            
            if result:
                return dict(result)
            return {"total_executions": 0, "avg_execution_time": 0, "total_tokens": 0}


# 同步版本的簡化介面（為了相容性）
class SyncDatabaseManager:
    """同步版本的資料庫管理器（簡化版）"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        # 在實際實作中，這裡會使用 psycopg2 或其他同步驅動
        # 目前先提供介面定義
    
    def get_active_prompt(self, user_id: str) -> Optional[Dict[str, Any]]:
        """獲取用戶活躍的 Prompt（同步版本）"""
        # TODO: 實作同步版本
        return None
    
    def save_user_prompt(self, user_id: str, name: str, content: str) -> bool:
        """儲存用戶 Prompt（同步版本）"""
        # TODO: 實作同步版本
        return True
    
    def activate_prompt(self, user_id: str, prompt_id: int) -> bool:
        """啟用特定 Prompt（同步版本）"""
        # TODO: 實作同步版本
        return True
    
    def get_user_prompts(self, user_id: str) -> List[Dict[str, Any]]:
        """獲取用戶所有 Prompt（同步版本）"""
        # TODO: 實作同步版本
        return []
    
    def delete_prompt(self, user_id: str, prompt_id: int) -> bool:
        """刪除 Prompt（同步版本）"""
        # TODO: 實作同步版本
        return True
    
    def get_contact_priority(self, user_id: str, sender_id: str) -> Dict[str, Any]:
        """獲取聯絡人優先級設定（同步版本）"""
        # TODO: 實作同步版本
        return {"priority_boost": 0, "is_starred": False}
    
    def set_contact_priority(self, user_id: str, sender_id: str, 
                           priority_boost: int, is_starred: bool) -> bool:
        """設定聯絡人優先級（同步版本）"""
        # TODO: 實作同步版本
        return True
    
    def log_agent_execution(self, log_data: Dict[str, Any]) -> bool:
        """記錄 Agent 執行日誌（同步版本）"""
        # TODO: 實作同步版本
        return True
    
    def get_execution_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """獲取執行統計（同步版本）"""
        # TODO: 實作同步版本
        return {"total_executions": 0, "avg_execution_time": 0, "total_tokens": 0} 
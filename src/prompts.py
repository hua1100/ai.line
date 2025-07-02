"""
System Prompt 管理模組
"""
import logging
from typing import Optional, Dict, Any
from jinja2 import Template, TemplateError
from .constants import DEFAULT_PROMPT_TEMPLATE
from .database import SyncDatabaseManager as DatabaseManager
from .schemas import ToneProfile

logger = logging.getLogger(__name__)


class PromptManager:
    """System Prompt 管理器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.default_template = DEFAULT_PROMPT_TEMPLATE
        self._template_cache = {}
    
    def get_user_prompt(self, user_id: str) -> str:
        """
        獲取用戶的活躍 Prompt，若無則返回預設模板
        
        Args:
            user_id: 使用者ID
            
        Returns:
            Prompt 模板字串
        """
        try:
            active_prompt = self.db.get_active_prompt(user_id)
            if active_prompt:
                logger.info(f"載入用戶 {user_id} 的自定 prompt: {active_prompt['name']}")
                return active_prompt['content']
            else:
                logger.info(f"用戶 {user_id} 無自定 prompt，使用預設模板")
                return self.default_template
        except Exception as e:
            logger.error(f"載入用戶 prompt 失敗: {e}")
            return self.default_template
    
    def save_user_prompt(self, user_id: str, name: str, content: str) -> bool:
        """
        儲存用戶自定 Prompt
        
        Args:
            user_id: 使用者ID
            name: Prompt 名稱
            content: Prompt 內容
            
        Returns:
            是否儲存成功
        """
        try:
            # 驗證 Prompt 內容
            if not self._validate_prompt_content(content):
                logger.error("Prompt 內容驗證失敗")
                return False
            
            # 儲存到資料庫
            success = self.db.save_user_prompt(user_id, name, content)
            if success:
                logger.info(f"成功儲存用戶 {user_id} 的 prompt: {name}")
                # 清除快取
                self._clear_cache(user_id)
            return success
        except Exception as e:
            logger.error(f"儲存用戶 prompt 失敗: {e}")
            return False
    
    def activate_prompt(self, user_id: str, prompt_id: int) -> bool:
        """
        啟用特定 Prompt
        
        Args:
            user_id: 使用者ID
            prompt_id: Prompt ID
            
        Returns:
            是否啟用成功
        """
        try:
            success = self.db.activate_prompt(user_id, prompt_id)
            if success:
                logger.info(f"成功啟用用戶 {user_id} 的 prompt ID: {prompt_id}")
                self._clear_cache(user_id)
            return success
        except Exception as e:
            logger.error(f"啟用 prompt 失敗: {e}")
            return False
    
    def render_prompt(self, template: str, tone_profile: ToneProfile) -> str:
        """
        使用 Jinja2 渲染 Prompt 模板
        
        Args:
            template: Prompt 模板
            tone_profile: 語調設定檔
            
        Returns:
            渲染後的 Prompt
        """
        try:
            # 檢查快取
            cache_key = hash(template + str(tone_profile.dict()))
            if cache_key in self._template_cache:
                return self._template_cache[cache_key]
            
            # 準備渲染變數
            render_vars = {
                'user_name': tone_profile.name,
                'user_profile': tone_profile.profile,
                'tone_style': tone_profile.style,
                'reply_length': tone_profile.reply_length,
                'signature': tone_profile.signature,
                'language': tone_profile.language
            }
            
            # 渲染模板
            jinja_template = Template(template)
            rendered = jinja_template.render(**render_vars)
            
            # 快取結果
            self._template_cache[cache_key] = rendered
            
            logger.debug(f"成功渲染 prompt 模板，長度: {len(rendered)}")
            return rendered
            
        except TemplateError as e:
            logger.error(f"Jinja2 模板渲染失敗: {e}")
            # 回退到預設模板
            return self._render_fallback_prompt(tone_profile)
        except Exception as e:
            logger.error(f"渲染 prompt 時發生未預期錯誤: {e}")
            return self._render_fallback_prompt(tone_profile)
    
    def get_prompt_variables(self, template: str) -> list:
        """
        解析模板中的變數
        
        Args:
            template: Prompt 模板
            
        Returns:
            變數名稱列表
        """
        try:
            from jinja2 import meta, Environment
            env = Environment()
            ast = env.parse(template)
            variables = meta.find_undeclared_variables(ast)
            return list(variables)
        except Exception as e:
            logger.error(f"解析模板變數失敗: {e}")
            return []
    
    def validate_template_syntax(self, template: str) -> tuple[bool, str]:
        """
        驗證模板語法
        
        Args:
            template: Prompt 模板
            
        Returns:
            (是否有效, 錯誤訊息)
        """
        try:
            Template(template)
            return True, ""
        except TemplateError as e:
            return False, str(e)
        except Exception as e:
            return False, f"未知錯誤: {str(e)}"
    
    def get_user_prompts(self, user_id: str) -> list:
        """
        獲取用戶所有 Prompt
        
        Args:
            user_id: 使用者ID
            
        Returns:
            Prompt 列表
        """
        try:
            return self.db.get_user_prompts(user_id)
        except Exception as e:
            logger.error(f"獲取用戶 prompts 失敗: {e}")
            return []
    
    def delete_prompt(self, user_id: str, prompt_id: int) -> bool:
        """
        刪除 Prompt
        
        Args:
            user_id: 使用者ID
            prompt_id: Prompt ID
            
        Returns:
            是否刪除成功
        """
        try:
            success = self.db.delete_prompt(user_id, prompt_id)
            if success:
                logger.info(f"成功刪除用戶 {user_id} 的 prompt ID: {prompt_id}")
                self._clear_cache(user_id)
            return success
        except Exception as e:
            logger.error(f"刪除 prompt 失敗: {e}")
            return False
    
    def _validate_prompt_content(self, content: str) -> bool:
        """
        驗證 Prompt 內容
        
        Args:
            content: Prompt 內容
            
        Returns:
            是否有效
        """
        # 基本長度檢查
        if len(content) < 10 or len(content) > 10000:
            return False
        
        # 檢查是否包含基本結構
        required_sections = ['Role', 'Goal', 'Tools', 'Constraint']
        content_upper = content.upper()
        
        for section in required_sections:
            if section.upper() not in content_upper:
                logger.warning(f"Prompt 缺少必要區段: {section}")
                # 不強制要求，只記錄警告
        
        # 檢查模板語法
        is_valid, error_msg = self.validate_template_syntax(content)
        if not is_valid:
            logger.error(f"Prompt 模板語法錯誤: {error_msg}")
            return False
        
        return True
    
    def _render_fallback_prompt(self, tone_profile: ToneProfile) -> str:
        """
        渲染備用 Prompt（當主要模板失敗時使用）
        
        Args:
            tone_profile: 語調設定檔
            
        Returns:
            簡化的 Prompt
        """
        fallback = f"""
你是 {tone_profile.name}。
請對訊息進行分類（工作/朋友/家人/廣告）、設定優先級（1-5）、
決定是否封存，並在需要時生成回覆草稿。
輸出格式為 JSON。語調：{tone_profile.style}。
"""
        return fallback
    
    def _clear_cache(self, user_id: str):
        """清除特定用戶的快取"""
        # 簡單清除所有快取，可以後續優化為更精確的清除
        self._template_cache.clear()
        logger.debug(f"已清除用戶 {user_id} 的 prompt 快取") 
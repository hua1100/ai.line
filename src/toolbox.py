"""
工具箱模組 - 定義五大核心工具
"""
import logging
import time
from typing import Dict, Any, List
try:
    from langchain_core.tools import tool
except ImportError:
    # 簡化版 tool 裝飾器
    def tool(func):
        return func

from .constants import CATEGORIES, DEFAULT_PRIORITY, AUTO_ARCHIVE_RULES
from .database import SyncDatabaseManager as DatabaseManager

logger = logging.getLogger(__name__)


@tool
def classify_tool(text: str) -> Dict[str, str]:
    """
    對訊息進行分類
    
    Args:
        text: 待分類的訊息內容
        
    Returns:
        包含分類結果的字典
    """
    start_time = time.time()
    
    try:
        # 這裡可以用簡單規則或呼叫 LLM
        # 目前使用關鍵字匹配作為示例
        text_lower = text.lower()
        
        if any(keyword in text for keyword in ['會議', '工作', '專案', '客戶', '報告', '截止', '任務']):
            category = "工作"
        elif any(keyword in text for keyword in ['媽', '爸', '爸爸', '媽媽', '家人', '回家', '家裡']):
            category = "家人"
        elif any(keyword in text for keyword in ['促銷', '優惠', '購買', '限時', '特價', '廣告', '推廣']):
            category = "廣告"
        else:
            category = "朋友"
        
        execution_time = time.time() - start_time
        logger.debug(f"classify_tool 執行完成，分類: {category}, 耗時: {execution_time:.3f}s")
        
        return {"category": category}
        
    except Exception as e:
        logger.error(f"classify_tool 執行失敗: {e}")
        return {"category": "朋友"}  # 預設分類


@tool
def priority_tool(sender_id: str, category: str) -> Dict[str, int]:
    """
    根據發送者和分類設定優先級
    
    Args:
        sender_id: 發送者ID
        category: 訊息分類
        
    Returns:
        包含優先級的字典 (1=最高, 5=最低)
    """
    start_time = time.time()
    
    try:
        # 從資料庫獲取聯絡人設定
        db = DatabaseManager()
        contact_settings = db.get_contact_priority(sender_id, sender_id)
        
        # 基礎優先級
        base_priority = DEFAULT_PRIORITY.get(category, 3)
        
        # 調整優先級
        priority_boost = contact_settings.get('priority_boost', 0)
        is_starred = contact_settings.get('is_starred', False)
        
        final_priority = base_priority + priority_boost
        
        # 星號聯絡人提升優先級
        if is_starred:
            final_priority = max(1, final_priority - 1)
        
        # 確保在有效範圍內
        final_priority = max(1, min(5, final_priority))
        
        execution_time = time.time() - start_time
        logger.debug(f"priority_tool 執行完成，優先級: {final_priority}, 耗時: {execution_time:.3f}s")
        
        return {"priority": final_priority}
        
    except Exception as e:
        logger.error(f"priority_tool 執行失敗: {e}")
        return {"priority": 3}  # 預設優先級


@tool
def archive_tool(category: str, priority: int) -> Dict[str, bool]:
    """
    決定是否自動封存訊息
    
    Args:
        category: 訊息分類
        priority: 優先級
        
    Returns:
        包含是否封存決定的字典
    """
    start_time = time.time()
    
    try:
        should_archive = False
        
        # 檢查自動封存規則
        if category in AUTO_ARCHIVE_RULES:
            rule = AUTO_ARCHIVE_RULES[category]
            if rule['enabled'] and priority >= rule['priority_threshold']:
                should_archive = True
        
        execution_time = time.time() - start_time
        logger.debug(f"archive_tool 執行完成，封存決定: {should_archive}, 耗時: {execution_time:.3f}s")
        
        return {"should_archive": should_archive}
        
    except Exception as e:
        logger.error(f"archive_tool 執行失敗: {e}")
        return {"should_archive": False}


@tool
def draft_reply_tool(text: str, tone_profile: Dict[str, Any]) -> Dict[str, str]:
    """
    生成回覆草稿
    
    Args:
        text: 原始訊息
        tone_profile: 語調設定檔
        
    Returns:
        包含草稿的字典
    """
    start_time = time.time()
    
    try:
        # 簡單的規則式回覆生成（實際應用中會用 LLM）
        text_lower = text.lower()
        style = tone_profile.get('style', '正式')
        signature = tone_profile.get('signature', '')
        
        draft = ""
        
        # 根據內容類型生成回覆
        if '?' in text or '嗎' in text:
            # 問句
            if style == '極簡':
                draft = "好"
            elif style == '輕鬆':
                draft = "可以啊！"
            else:
                draft = "好的，沒問題。"
        elif any(keyword in text for keyword in ['謝謝', '感謝']):
            # 感謝
            if style == '極簡':
                draft = "不客氣"
            else:
                draft = "不用客氣！"
        elif any(keyword in text for keyword in ['會議', '開會']):
            # 會議相關
            draft = "收到，我會準時參加。"
        else:
            # 一般回覆
            if style == '極簡':
                draft = "收到"
            elif style == '輕鬆':
                draft = "了解！"
            else:
                draft = "好的，我知道了。"
        
        # 加上簽名
        if signature and signature.strip():
            draft += f" {signature}"
        
        execution_time = time.time() - start_time
        logger.debug(f"draft_reply_tool 執行完成，草稿長度: {len(draft)}, 耗時: {execution_time:.3f}s")
        
        return {"draft": draft}
        
    except Exception as e:
        logger.error(f"draft_reply_tool 執行失敗: {e}")
        return {"draft": "收到"}


@tool
def sort_tool(threads: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    對對話串進行多因子排序
    
    Args:
        threads: 對話串列表
        
    Returns:
        包含排序後 thread_id 列表的字典
    """
    start_time = time.time()
    
    try:
        # 多因子排序：優先級 > 時間戳 > 未讀數
        def sort_key(thread):
            priority = thread.get('priority', 3)
            timestamp = thread.get('last_message_at', '1970-01-01T00:00:00Z')
            unread_count = thread.get('unread_count', 0)
            
            # 優先級越小越重要，時間戳越新越重要
            return (priority, -int(timestamp.replace('-', '').replace(':', '').replace('T', '').replace('Z', '')), -unread_count)
        
        sorted_threads = sorted(threads, key=sort_key)
        sorted_ids = [thread['id'] for thread in sorted_threads]
        
        execution_time = time.time() - start_time
        logger.debug(f"sort_tool 執行完成，排序 {len(sorted_ids)} 個對話串, 耗時: {execution_time:.3f}s")
        
        return {"sorted_threads": sorted_ids}
        
    except Exception as e:
        logger.error(f"sort_tool 執行失敗: {e}")
        # 回傳原始順序
        original_ids = [thread.get('id', f'thread_{i}') for i, thread in enumerate(threads)]
        return {"sorted_threads": original_ids}


@tool
def tag_tool(text: str) -> Dict[str, List[str]]:
    """
    為訊息生成標籤
    
    Args:
        text: 訊息內容
        
    Returns:
        包含標籤列表的字典
    """
    start_time = time.time()
    
    try:
        tags = []
        text_lower = text.lower()
        
        # 關鍵字標籤映射
        keyword_tags = {
            '會議': ['會議', '工作'],
            '電影': ['電影', '娛樂'],
            '吃飯': ['聚餐', '美食'],
            '生日': ['生日', '慶祝'],
            '旅行': ['旅遊', '出遊'],
            '購物': ['購物', '消費'],
            '運動': ['運動', '健身'],
            '學習': ['學習', '教育'],
            '醫院': ['健康', '醫療'],
            '緊急': ['緊急', '重要']
        }
        
        # 提取關鍵字標籤
        for keyword, related_tags in keyword_tags.items():
            if keyword in text:
                tags.extend(related_tags)
        
        # 去重並限制數量
        tags = list(set(tags))[:5]
        
        # 如果沒有標籤，給個通用標籤
        if not tags:
            tags = ['一般']
        
        execution_time = time.time() - start_time
        logger.debug(f"tag_tool 執行完成，標籤: {tags}, 耗時: {execution_time:.3f}s")
        
        return {"tags": tags}
        
    except Exception as e:
        logger.error(f"tag_tool 執行失敗: {e}")
        return {"tags": ["一般"]}


def get_all_tools():
    """獲取所有可用工具"""
    tools = [
        classify_tool,
        priority_tool,
        archive_tool,
        draft_reply_tool,
        sort_tool,
        tag_tool
    ]
    
    logger.info(f"載入 {len(tools)} 個工具")
    return tools


def get_tool_by_name(tool_name: str):
    """根據名稱獲取特定工具"""
    tool_map = {
        'classify_tool': classify_tool,
        'priority_tool': priority_tool,
        'archive_tool': archive_tool,
        'draft_reply_tool': draft_reply_tool,
        'sort_tool': sort_tool,
        'tag_tool': tag_tool
    }
    
    tool = tool_map.get(tool_name)
    if not tool:
        logger.warning(f"找不到工具: {tool_name}")
    
    return tool 
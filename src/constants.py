"""
系統常量定義
"""

# 訊息分類常量
CATEGORIES = [
    "工作",
    "朋友", 
    "家人",
    "廣告"
]

# 優先級等級 (1=最高, 5=最低)
PRIORITY_LEVELS = [1, 2, 3, 4, 5]

# 預設優先級設定
DEFAULT_PRIORITY = {
    "工作": 2,
    "朋友": 3,
    "家人": 1,
    "廣告": 5
}

# 語調風格選項
TONE_STYLES = [
    "正式",
    "輕鬆",
    "極簡",
    "詳細",
    "幽默",
    "專業"
]

# 回覆長度偏好
REPLY_LENGTH_OPTIONS = [
    "極簡",      # <10 字
    "簡短",      # 10-30 字
    "適中",      # 30-80 字
    "詳細"       # >80 字
]

# 語言選項
SUPPORTED_LANGUAGES = [
    "zh-tw",     # 繁體中文
    "zh-cn",     # 簡體中文
    "en",        # 英文
    "ja",        # 日文
    "ko"         # 韓文
]

# 自動封存規則
AUTO_ARCHIVE_RULES = {
    "廣告": {
        "priority_threshold": 4,  # 優先級 >= 4 的廣告自動封存
        "enabled": True
    },
    "工作": {
        "priority_threshold": 5,  # 只有最低優先級工作訊息才封存
        "enabled": False
    }
}

# Tool 相關常量
TOOL_NAMES = [
    "classify_tool",
    "priority_tool", 
    "archive_tool",
    "draft_reply_tool",
    "sort_tool"
]

# 預設 System Prompt 模板路徑
DEFAULT_PROMPT_TEMPLATE = """
# Role
你是 {{user_name}}，{{user_profile}}。你的主要任務是協助處理通訊訊息。

# Goal  
對收到的訊息進行以下處理：
1. 分類到四大類別：工作、朋友、家人、廣告
2. 根據發送者設定優先級 (1-5)
3. 判斷是否需要封存
4. 必要時生成符合個人風格的回覆草稿

# Tools
你有以下工具可用：
- classify: 判斷訊息類別
- priority: 設定優先級  
- archive: 決定是否封存
- draft_reply: 生成回覆草稿

# Constraint
- 輸出格式必須為有效 JSON
- 語言：{{language}}
- 語調風格：{{tone_style}}
- 回覆字數：{{reply_length}}
- 個人簽名：{{signature}}

# Example
輸入："今晚一起去看電影《沙丘2》好嗎？"
輸出：
{
  "category": "朋友",
  "priority": 2,
  "should_archive": false,
  "draft": "可以啊，幾點開場？{{signature}}"
}
"""

# 錯誤訊息常量
ERROR_MESSAGES = {
    "INVALID_CATEGORY": "無效的訊息分類",
    "INVALID_PRIORITY": "優先級必須在 1-5 之間",
    "PROMPT_NOT_FOUND": "找不到指定的 Prompt",
    "USER_NOT_FOUND": "找不到指定的使用者",
    "TOOL_EXECUTION_FAILED": "工具執行失敗",
    "JSON_PARSE_ERROR": "JSON 格式解析錯誤",
    "OPENAI_API_ERROR": "OpenAI API 呼叫失敗",
    "DATABASE_ERROR": "資料庫操作失敗"
}

# API 限制
API_LIMITS = {
    "MAX_MESSAGE_LENGTH": 5000,      # 最大訊息長度
    "MAX_PROMPT_LENGTH": 10000,      # 最大 Prompt 長度
    "MAX_PROMPTS_PER_USER": 10,      # 每位使用者最多 Prompt 數量
    "RATE_LIMIT_PER_MINUTE": 100     # 每分鐘 API 呼叫限制
}

# 效能監控
PERFORMANCE_THRESHOLDS = {
    "MAX_TOOL_EXECUTION_TIME": 5.0,  # 單一工具最大執行時間（秒）
    "MAX_TOTAL_EXECUTION_TIME": 15.0, # 總執行時間上限（秒）
    "TOKEN_WARNING_THRESHOLD": 1000   # Token 使用量警告閾值
} 
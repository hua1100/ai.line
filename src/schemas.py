"""
資料模型定義 - 使用 Pydantic 進行資料驗證
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ToneProfile(BaseModel):
    """語調設定檔"""
    name: str = Field(..., description="使用者姓名")
    profile: str = Field("", description="個人簡介")
    style: str = Field("正式", description="語調風格")
    reply_length: str = Field("簡短", description="回覆長度偏好")
    signature: str = Field("", description="個人簽名")
    language: str = Field("zh-tw", description="語言設定")


class MessageRequest(BaseModel):
    """訊息處理請求"""
    text: str = Field(..., description="待處理的訊息內容")
    sender_id: str = Field(..., description="發送者ID")
    tone_profile: ToneProfile = Field(..., description="語調設定")


class OrganizeResponse(BaseModel):
    """訊息處理回應"""
    category: str = Field(..., description="訊息分類")
    tags: List[str] = Field(..., description="標籤列表")
    priority: int = Field(..., ge=1, le=5, description="優先級 (1-5)")
    should_archive: bool = Field(..., description="是否應該封存")
    draft: Optional[str] = Field(None, description="回覆草稿")


class PromptData(BaseModel):
    """System Prompt 資料"""
    name: str = Field(..., max_length=100, description="Prompt 名稱")
    content: str = Field(..., description="Prompt 內容")
    is_active: bool = Field(False, description="是否為活躍 Prompt")


class PromptResponse(BaseModel):
    """Prompt 查詢回應"""
    id: int = Field(..., description="Prompt ID")
    user_id: str = Field(..., description="使用者ID")
    name: str = Field(..., description="Prompt 名稱")
    content: str = Field(..., description="Prompt 內容")
    is_active: bool = Field(..., description="是否為活躍 Prompt")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: datetime = Field(..., description="更新時間")


class PromptCreateRequest(BaseModel):
    """建立 Prompt 請求"""
    name: str = Field(..., max_length=100, description="Prompt 名稱")
    content: str = Field(..., description="Prompt 內容")


class PromptUpdateRequest(BaseModel):
    """更新 Prompt 請求"""
    content: str = Field(..., description="Prompt 內容")


class ContactPriority(BaseModel):
    """聯絡人優先級設定"""
    sender_id: str = Field(..., description="聯絡人ID")
    priority_boost: int = Field(0, ge=-2, le=2, description="優先級調整 (-2 到 +2)")
    is_starred: bool = Field(False, description="是否為星號聯絡人")


class ToolResult(BaseModel):
    """工具執行結果"""
    tool_name: str = Field(..., description="工具名稱")
    input_data: Dict[str, Any] = Field(..., description="輸入資料")
    output_data: Dict[str, Any] = Field(..., description="輸出資料")
    execution_time: float = Field(..., description="執行時間（秒）")
    success: bool = Field(..., description="是否執行成功")
    error_message: Optional[str] = Field(None, description="錯誤訊息")


class AgentExecutionLog(BaseModel):
    """Agent 執行日誌"""
    user_id: str = Field(..., description="使用者ID")
    message_text: str = Field(..., description="原始訊息")
    prompt_used: str = Field(..., description="使用的 Prompt")
    tool_results: List[ToolResult] = Field(..., description="工具執行結果")
    final_response: OrganizeResponse = Field(..., description="最終回應")
    total_execution_time: float = Field(..., description="總執行時間")
    token_usage: Dict[str, int] = Field(..., description="Token 使用量")
    timestamp: datetime = Field(..., description="執行時間戳")


class ErrorResponse(BaseModel):
    """錯誤回應"""
    error: str = Field(..., description="錯誤類型")
    message: str = Field(..., description="錯誤訊息")
    details: Optional[Dict[str, Any]] = Field(None, description="錯誤詳情") 
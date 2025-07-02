"""
FastAPI 入口點 - 簡化版本用於測試
"""
import logging
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .schemas import MessageRequest, ToneProfile
from .toolbox import classify_tool, tag_tool, priority_tool, archive_tool, draft_reply_tool
from .demo_storage import demo_storage

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 建立 FastAPI 應用
app = FastAPI(
    title="AI Messenger Agent",
    description="基於規則的通訊訊息處理助手",
    version="1.0.0"
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路徑 - 健康檢查"""
    return {
        "message": "AI Messenger Agent is running!",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """詳細健康檢查"""
    return {
        "status": "healthy",
        "database_configured": bool(settings.database_url),
        "openai_configured": bool(settings.openai_api_key),
        "tools_available": 5
    }


@app.post("/organize")
async def organize_message(request: MessageRequest):
    """
    處理訊息 - 分類、優先級、封存決定、回覆草稿
    """
    try:
        logger.info(f"收到訊息處理請求，發送者: {request.sender_id}")
        
        # 1. 分類
        classify_result = classify_tool(request.text)
        category = classify_result["category"]
        
        # 2. 標籤
        tag_result = tag_tool(request.text)
        tags = tag_result["tags"]
        
        # 3. 優先級
        priority_result = priority_tool(request.sender_id, category)
        priority = priority_result["priority"]
        
        # 4. 封存決定
        archive_result = archive_tool(category, priority)
        should_archive = archive_result["should_archive"]
        
        # 5. 回覆草稿
        tone_profile_dict = request.tone_profile.dict()
        draft_result = draft_reply_tool(request.text, tone_profile_dict)
        draft = draft_result.get("draft")
        
        result = {
            "category": category,
            "tags": tags,
            "priority": priority,
            "should_archive": should_archive,
            "draft": draft
        }
        
        logger.info(f"訊息處理完成: {category}, 優先級: {priority}")
        return result
        
    except Exception as e:
        logger.error(f"處理訊息時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"處理訊息失敗: {str(e)}")


@app.post("/test")
async def test_tools():
    """測試所有工具"""
    test_message = "今晚一起去看電影《沙丘2》好嗎？"
    test_tone = {
        "name": "測試用戶",
        "style": "輕鬆",
        "signature": "- 小明"
    }
    
    try:
        classify_result = classify_tool(test_message)
        tag_result = tag_tool(test_message)
        priority_result = priority_tool("test_user", classify_result["category"])
        archive_result = archive_tool(classify_result["category"], priority_result["priority"])
        draft_result = draft_reply_tool(test_message, test_tone)
        
        return {
            "test_message": test_message,
            "classify": classify_result,
            "tags": tag_result,
            "priority": priority_result,
            "archive": archive_result,
            "draft": draft_result,
            "status": "所有工具運作正常"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"工具測試失敗: {str(e)}")


# =============================================================================
# Demo 相關端點
# =============================================================================

@app.get("/demo/messages")
async def get_demo_messages():
    """獲取所有 Demo 訊息"""
    try:
        messages = demo_storage.get_all_messages()
        unprocessed = demo_storage.get_unprocessed_messages()
        
        return {
            "total_messages": len(messages),
            "unprocessed_count": len(unprocessed),
            "messages": messages
        }
    except Exception as e:
        logger.error(f"獲取 Demo 訊息失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取訊息失敗: {str(e)}")


@app.get("/demo/messages/unprocessed")
async def get_unprocessed_messages():
    """獲取未處理的訊息"""
    try:
        messages = demo_storage.get_unprocessed_messages()
        return {
            "count": len(messages),
            "messages": messages
        }
    except Exception as e:
        logger.error(f"獲取未處理訊息失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取未處理訊息失敗: {str(e)}")


@app.post("/demo/process/{message_id}")
async def process_demo_message(message_id: int):
    """處理指定的 Demo 訊息"""
    try:
        target_message = demo_storage.get_message_by_id(message_id)
        
        if not target_message:
            raise HTTPException(status_code=404, detail="訊息不存在")
        
        if target_message.get("processed", False):
            return {
                "message": "訊息已處理過",
                "result": target_message.get("processing_result")
            }
        
        # 獲取用戶設定檔
        user_profile = demo_storage.get_user_profile()
        
        # 建立處理請求
        tone_profile = ToneProfile(
            name=user_profile["name"],
            profile=user_profile["profile"],
            style=user_profile["tone_style"],
            reply_length=user_profile["reply_length"],
            signature=user_profile["signature"],
            language=user_profile["language"]
        )
        
        request = MessageRequest(
            text=target_message["text"],
            sender_id=target_message["sender_id"],
            tone_profile=tone_profile
        )
        
        # 處理訊息（重用現有邏輯）
        result = await organize_message(request)
        
        # 標記為已處理
        demo_storage.mark_message_processed(message_id, result)
        
        # 記錄處理日誌
        demo_storage.log_processing(message_id, {
            "request": request.dict(),
            "final_response": result,
            "total_execution_time": 1.0  # 簡化版
        })
        
        return {
            "message_id": message_id,
            "original_text": target_message["text"],
            "sender": target_message["sender_name"],
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"處理 Demo 訊息失敗: {e}")
        raise HTTPException(status_code=500, detail=f"處理訊息失敗: {str(e)}")


@app.post("/demo/batch-process")
async def batch_process_unprocessed():
    """批次處理所有未處理的訊息"""
    try:
        unprocessed = demo_storage.get_unprocessed_messages()
        results = []
        
        for msg in unprocessed:
            try:
                result = await process_demo_message(msg["id"])
                results.append({
                    "success": True,
                    "message_id": msg["id"],
                    "sender": msg["sender_name"],
                    "result": result
                })
            except Exception as e:
                results.append({
                    "success": False,
                    "message_id": msg["id"],
                    "sender": msg.get("sender_name", "未知"),
                    "error": str(e)
                })
        
        return {
            "processed_count": len([r for r in results if r["success"]]),
            "failed_count": len([r for r in results if not r["success"]]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"批次處理失敗: {e}")
        raise HTTPException(status_code=500, detail=f"批次處理失敗: {str(e)}")


@app.get("/demo/stats")
async def get_demo_stats():
    """獲取 Demo 統計資料"""
    try:
        stats = demo_storage.get_processing_stats()
        messages = demo_storage.get_all_messages()
        contacts = demo_storage.load_json("contacts")
        
        return {
            "processing_stats": stats,
            "total_messages": len(messages),
            "total_contacts": len(contacts),
            "unprocessed_count": len(demo_storage.get_unprocessed_messages())
        }
    except Exception as e:
        logger.error(f"獲取統計失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取統計失敗: {str(e)}")


@app.post("/demo/add-message")
async def add_demo_message(text: str, sender_id: str, sender_name: str):
    """新增 Demo 訊息"""
    try:
        message_id = demo_storage.add_message(text, sender_id, sender_name)
        return {
            "message": "訊息新增成功",
            "message_id": message_id,
            "text": text,
            "sender": sender_name
        }
    except Exception as e:
        logger.error(f"新增 Demo 訊息失敗: {e}")
        raise HTTPException(status_code=500, detail=f"新增訊息失敗: {str(e)}")


@app.get("/demo/contacts")
async def get_demo_contacts():
    """獲取所有聯絡人資料"""
    try:
        contacts = demo_storage.load_json("contacts")
        return {
            "total_contacts": len(contacts),
            "contacts": contacts
        }
    except Exception as e:
        logger.error(f"獲取聯絡人失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取聯絡人失敗: {str(e)}")


@app.get("/demo/user-profile")
async def get_demo_user_profile():
    """獲取用戶設定檔"""
    try:
        profile = demo_storage.get_user_profile()
        return {
            "user_profile": profile
        }
    except Exception as e:
        logger.error(f"獲取用戶設定檔失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取用戶設定檔失敗: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)

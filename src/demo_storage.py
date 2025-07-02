"""
Demo 專用的簡單 JSON 檔案儲存系統
不需要資料庫，適合快速展示和測試
"""
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

class DemoStorage:
    """Demo 用的資料儲存類別"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.ensure_data_dir()
        self.init_demo_data()
    
    def ensure_data_dir(self):
        """確保資料目錄存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"✅ 建立資料目錄: {self.data_dir}")
    
    def load_json(self, filename: str) -> Dict:
        """載入 JSON 檔案"""
        filepath = os.path.join(self.data_dir, f"{filename}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_json(self, filename: str, data: Dict):
        """儲存到 JSON 檔案"""
        filepath = os.path.join(self.data_dir, f"{filename}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def init_demo_data(self):
        """初始化空的 Demo 資料結構（如果檔案不存在）"""
        
        # 1. Demo 訊息資料模板
        if not os.path.exists(os.path.join(self.data_dir, "demo_messages.json")):
            demo_messages = {
                "messages": []
            }
            self.save_json("demo_messages", demo_messages)
        
        # 2. 聯絡人資料模板
        if not os.path.exists(os.path.join(self.data_dir, "contacts.json")):
            contacts_data = {}
            self.save_json("contacts", contacts_data)
        
        # 3. 用戶設定檔模板
        if not os.path.exists(os.path.join(self.data_dir, "user_profiles.json")):
            user_profiles = {
                "demo_user": {
                    "name": "Demo 用戶",
                    "profile": "",
                    "tone_style": "正式",
                    "reply_length": "簡短",
                    "signature": "",
                    "language": "zh-tw"
                }
            }
            self.save_json("user_profiles", user_profiles)
        
        # 4. 處理歷史記錄模板
        if not os.path.exists(os.path.join(self.data_dir, "processing_history.json")):
            processing_history = {
                "logs": []
            }
            self.save_json("processing_history", processing_history)
    
    # 訊息相關方法
    def get_all_messages(self) -> List[Dict]:
        """獲取所有 demo 訊息"""
        return self.load_json("demo_messages").get("messages", [])
    
    def get_unprocessed_messages(self) -> List[Dict]:
        """獲取未處理的訊息"""
        messages = self.get_all_messages()
        return [msg for msg in messages if not msg.get("processed", False)]
    
    def get_message_by_id(self, message_id: int) -> Optional[Dict]:
        """根據 ID 獲取訊息"""
        messages = self.get_all_messages()
        for msg in messages:
            if msg["id"] == message_id:
                return msg
        return None
    
    def mark_message_processed(self, message_id: int, result: Dict):
        """標記訊息為已處理"""
        data = self.load_json("demo_messages")
        for msg in data["messages"]:
            if msg["id"] == message_id:
                msg["processed"] = True
                msg["processing_result"] = result
                msg["processed_at"] = datetime.now().isoformat()
                break
        self.save_json("demo_messages", data)
    
    def add_message(self, text: str, sender_id: str, sender_name: str) -> int:
        """新增新訊息"""
        data = self.load_json("demo_messages")
        new_id = max([msg["id"] for msg in data["messages"]], default=0) + 1
        
        new_message = {
            "id": new_id,
            "text": text,
            "sender_id": sender_id,
            "sender_name": sender_name,
            "timestamp": datetime.now().isoformat(),
            "processed": False
        }
        
        data["messages"].append(new_message)
        self.save_json("demo_messages", data)
        return new_id
    
    # 聯絡人相關方法
    def get_contact_info(self, sender_id: str) -> Dict:
        """獲取聯絡人資訊"""
        contacts = self.load_json("contacts")
        return contacts.get(sender_id, {
            "name": sender_id,
            "priority_boost": 0,
            "is_starred": False,
            "category_hint": "朋友"
        })
    
    def update_contact(self, sender_id: str, **kwargs):
        """更新聯絡人資料"""
        contacts = self.load_json("contacts")
        if sender_id not in contacts:
            contacts[sender_id] = {"name": sender_id}
        
        contacts[sender_id].update(kwargs)
        contacts[sender_id]["updated_at"] = datetime.now().isoformat()
        self.save_json("contacts", contacts)
    
    # 用戶設定檔相關
    def get_user_profile(self, user_id: str = "demo_user") -> Dict:
        """獲取用戶設定檔"""
        profiles = self.load_json("user_profiles")
        return profiles.get(user_id, {
            "name": "Demo 用戶",
            "profile": "",
            "tone_style": "正式", 
            "reply_length": "簡短",
            "signature": "",
            "language": "zh-tw"
        })
    
    def update_user_profile(self, user_id: str, **kwargs):
        """更新用戶設定檔"""
        profiles = self.load_json("user_profiles")
        if user_id not in profiles:
            profiles[user_id] = {}
        
        profiles[user_id].update(kwargs)
        profiles[user_id]["updated_at"] = datetime.now().isoformat()
        self.save_json("user_profiles", profiles)
    
    # 處理記錄相關
    def log_processing(self, message_id: int, processing_data: Dict):
        """記錄處理過程"""
        history = self.load_json("processing_history")
        
        log_entry = {
            "id": str(uuid.uuid4()),
            "message_id": message_id,
            "timestamp": datetime.now().isoformat(),
            **processing_data
        }
        
        history["logs"].append(log_entry)
        self.save_json("processing_history", history)
    
    def get_processing_stats(self) -> Dict:
        """獲取處理統計"""
        history = self.load_json("processing_history")
        logs = history.get("logs", [])
        
        total_processed = len(logs)
        if total_processed == 0:
            return {"total_processed": 0}
        
        # 統計分類分佈
        categories = {}
        avg_execution_time = 0
        
        for log in logs:
            result = log.get("final_response", {})
            category = result.get("category", "未知")
            categories[category] = categories.get(category, 0) + 1
            
            exec_time = log.get("total_execution_time", 0)
            avg_execution_time += exec_time
        
        avg_execution_time = avg_execution_time / total_processed if total_processed > 0 else 0
        
        return {
            "total_processed": total_processed,
            "category_distribution": categories,
            "avg_execution_time": avg_execution_time
        }

# 全域實例
demo_storage = DemoStorage() 
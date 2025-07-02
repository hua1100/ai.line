#!/usr/bin/env python3
"""
快速建立 Demo 範例資料的腳本
運行此腳本將在 data/ 目錄建立完整的範例資料
"""

import os
import json
from datetime import datetime, timedelta

def create_sample_data():
    """建立完整的範例資料"""
    
    # 確保 data 目錄存在
    if not os.path.exists("data"):
        os.makedirs("data")
        print("✅ 建立 data 目錄")
    
    # 1. 建立範例訊息
    demo_messages = {
        "messages": [
            {
                "id": 1,
                "text": "明天下午的會議記得帶那個項目提案書，我們要向客戶簡報新的設計方案",
                "sender_id": "boss_001",
                "sender_name": "王經理",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "processed": False
            },
            {
                "id": 2,
                "text": "今晚一起去看《沙丘2》？IMAX 場次 19:30 開場，我已經買好票了",
                "sender_id": "friend_002",
                "sender_name": "小李",
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "processed": False
            },
            {
                "id": 3,
                "text": "週末回家吃飯嗎？媽媽做你最愛吃的糖醋排骨，爸爸說很想你了",
                "sender_id": "family_003",
                "sender_name": "媽媽",
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "processed": False
            },
            {
                "id": 4,
                "text": "🎉新年限時優惠！iPhone 15 Pro 現在只要 $28,999，免運費直送到府！點擊連結立即搶購 → http://fake-deal.com",
                "sender_id": "spam_004",
                "sender_name": "科技商城",
                "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(),
                "processed": False
            },
            {
                "id": 5,
                "text": "資料庫備份作業已完成，今日共處理 15,432 筆用戶資料，請確認報表是否正常",
                "sender_id": "system_005",
                "sender_name": "系統管理員",
                "timestamp": datetime.now().isoformat(),
                "processed": False
            },
            {
                "id": 6,
                "text": "週五下班後要不要一起去新開的那家燒烤店？聽說蠻好吃的",
                "sender_id": "colleague_006",
                "sender_name": "同事小張",
                "timestamp": datetime.now().isoformat(),
                "processed": False
            }
        ]
    }
    
    # 2. 建立聯絡人資料
    contacts_data = {
        "boss_001": {
            "name": "王經理",
            "priority_boost": 1,
            "is_starred": True,
            "category_hint": "工作",
            "updated_at": datetime.now().isoformat()
        },
        "friend_002": {
            "name": "小李",
            "priority_boost": 0,
            "is_starred": False,
            "category_hint": "朋友",
            "updated_at": datetime.now().isoformat()
        },
        "family_003": {
            "name": "媽媽",
            "priority_boost": 2,
            "is_starred": True,
            "category_hint": "家人",
            "updated_at": datetime.now().isoformat()
        },
        "spam_004": {
            "name": "科技商城",
            "priority_boost": -2,
            "is_starred": False,
            "category_hint": "廣告",
            "updated_at": datetime.now().isoformat()
        },
        "system_005": {
            "name": "系統管理員",
            "priority_boost": 1,
            "is_starred": False,
            "category_hint": "工作",
            "updated_at": datetime.now().isoformat()
        },
        "colleague_006": {
            "name": "同事小張",
            "priority_boost": 0,
            "is_starred": False,
            "category_hint": "朋友",
            "updated_at": datetime.now().isoformat()
        }
    }
    
    # 3. 建立用戶設定檔
    user_profiles = {
        "demo_user": {
            "name": "小王",
            "profile": "軟體工程師，喜歡看電影和閱讀科技文章",
            "tone_style": "輕鬆",
            "reply_length": "簡短",
            "signature": "- 小王",
            "language": "zh-tw",
            "updated_at": datetime.now().isoformat()
        }
    }
    
    # 4. 建立空的處理歷史記錄
    processing_history = {
        "logs": []
    }
    
    # 儲存所有檔案
    files_to_save = [
        ("demo_messages.json", demo_messages),
        ("contacts.json", contacts_data),
        ("user_profiles.json", user_profiles),
        ("processing_history.json", processing_history)
    ]
    
    for filename, data in files_to_save:
        filepath = os.path.join("data", filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ 建立 {filename}")
    
    print(f"\n🎉 範例資料建立完成！")
    print(f"📁 資料位置: {os.path.abspath('data')}")
    print(f"📊 訊息數量: {len(demo_messages['messages'])}")
    print(f"👥 聯絡人數量: {len(contacts_data)}")
    print(f"\n🚀 現在可以啟動伺服器測試:")
    print(f"   ./start.sh")
    print(f"\n🌐 然後訪問:")
    print(f"   http://localhost:8000/demo/messages")

if __name__ == "__main__":
    create_sample_data() 
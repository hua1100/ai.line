# JSON 資料格式說明

Demo 系統使用 JSON 檔案儲存資料，所有檔案位於 `data/` 目錄下。

## 📁 檔案結構

```
data/
├── demo_messages.json      # 訊息資料
├── contacts.json           # 聯絡人資料
├── user_profiles.json      # 用戶設定檔
└── processing_history.json # 處理歷史記錄
```

## 📄 檔案格式詳細說明

### 1. demo_messages.json - 訊息資料

```json
{
  "messages": [
    {
      "id": 1,
      "text": "訊息內容",
      "sender_id": "發送者ID",
      "sender_name": "發送者姓名",
      "timestamp": "2024-01-15T14:30:00",
      "processed": false,
      "processing_result": {
        "category": "工作",
        "tags": ["會議", "重要"],
        "priority": 2,
        "should_archive": false,
        "draft": "回覆草稿內容"
      },
      "processed_at": "2024-01-15T14:35:00"
    }
  ]
}
```

**欄位說明**：
- `id` (整數): 訊息唯一識別碼
- `text` (字串): 訊息內容
- `sender_id` (字串): 發送者唯一識別碼
- `sender_name` (字串): 發送者顯示名稱
- `timestamp` (ISO 時間): 訊息建立時間
- `processed` (布林): 是否已處理
- `processing_result` (物件): 處理結果（當 processed=true 時）
- `processed_at` (ISO 時間): 處理完成時間

### 2. contacts.json - 聯絡人資料

```json
{
  "sender_id_001": {
    "name": "聯絡人姓名",
    "priority_boost": 1,
    "is_starred": true,
    "category_hint": "工作",
    "updated_at": "2024-01-15T10:00:00"
  },
  "sender_id_002": {
    "name": "另一個聯絡人",
    "priority_boost": 0,
    "is_starred": false,
    "category_hint": "朋友",
    "updated_at": "2024-01-15T11:00:00"
  }
}
```

**欄位說明**：
- `name` (字串): 聯絡人顯示名稱
- `priority_boost` (整數): 優先級調整 (-2 到 +2)
- `is_starred` (布林): 是否為星號聯絡人
- `category_hint` (字串): 分類提示 (工作/朋友/家人/廣告)
- `updated_at` (ISO 時間): 最後更新時間

### 3. user_profiles.json - 用戶設定檔

```json
{
  "demo_user": {
    "name": "用戶姓名",
    "profile": "個人簡介描述",
    "tone_style": "輕鬆",
    "reply_length": "簡短",
    "signature": "- 小王",
    "language": "zh-tw",
    "updated_at": "2024-01-15T09:00:00"
  },
  "user_002": {
    "name": "另一個用戶",
    "profile": "軟體工程師，喜歡電影",
    "tone_style": "正式",
    "reply_length": "適中",
    "signature": "Best regards, John",
    "language": "en",
    "updated_at": "2024-01-15T09:30:00"
  }
}
```

**欄位說明**：
- `name` (字串): 用戶姓名
- `profile` (字串): 個人簡介
- `tone_style` (字串): 語調風格 (正式/輕鬆/極簡/詳細/幽默/專業)
- `reply_length` (字串): 回覆長度偏好 (極簡/簡短/適中/詳細)
- `signature` (字串): 個人簽名
- `language` (字串): 語言設定 (zh-tw/zh-cn/en/ja/ko)
- `updated_at` (ISO 時間): 最後更新時間

### 4. processing_history.json - 處理歷史記錄

```json
{
  "logs": [
    {
      "id": "uuid-string",
      "message_id": 1,
      "timestamp": "2024-01-15T14:35:00",
      "request": {
        "text": "原始訊息內容",
        "sender_id": "sender_001",
        "tone_profile": {
          "name": "小王",
          "style": "輕鬆",
          "signature": "- 小王"
        }
      },
      "final_response": {
        "category": "工作",
        "tags": ["會議"],
        "priority": 2,
        "should_archive": false,
        "draft": "好的，沒問題"
      },
      "total_execution_time": 1.234
    }
  ]
}
```

**欄位說明**：
- `id` (字串): 日誌唯一識別碼 (UUID)
- `message_id` (整數): 對應的訊息 ID
- `timestamp` (ISO 時間): 處理時間
- `request` (物件): 原始請求內容
- `final_response` (物件): 最終處理結果
- `total_execution_time` (浮點數): 總執行時間（秒）

## 🎯 範例資料模板

### 訊息範例

```json
{
  "messages": [
    {
      "id": 1,
      "text": "明天下午的會議記得帶那個項目提案書",
      "sender_id": "boss_001",
      "sender_name": "王經理",
      "timestamp": "2024-01-15T14:30:00",
      "processed": false
    },
    {
      "id": 2,
      "text": "今晚一起去看《沙丘2》？",
      "sender_id": "friend_002",
      "sender_name": "小李",
      "timestamp": "2024-01-15T18:00:00",
      "processed": false
    },
    {
      "id": 3,
      "text": "週末回家吃飯嗎？媽媽做你愛吃的糖醋排骨",
      "sender_id": "family_003",
      "sender_name": "媽媽",
      "timestamp": "2024-01-15T19:15:00",
      "processed": false
    },
    {
      "id": 4,
      "text": "🎉限時優惠！iPhone 15 現在只要$999，立即購買享免運費！",
      "sender_id": "spam_004",
      "sender_name": "科技商城",
      "timestamp": "2024-01-15T20:30:00",
      "processed": false
    }
  ]
}
```

### 聯絡人範例

```json
{
  "boss_001": {
    "name": "王經理",
    "priority_boost": 1,
    "is_starred": true,
    "category_hint": "工作"
  },
  "friend_002": {
    "name": "小李",
    "priority_boost": 0,
    "is_starred": false,
    "category_hint": "朋友"
  },
  "family_003": {
    "name": "媽媽",
    "priority_boost": 2,
    "is_starred": true,
    "category_hint": "家人"
  },
  "spam_004": {
    "name": "科技商城",
    "priority_boost": -2,
    "is_starred": false,
    "category_hint": "廣告"
  }
}
```

## 🔧 使用方式

1. **建立範例資料**：複製上述範例到對應的 JSON 檔案中
2. **啟動伺服器**：運行 `./start.sh`
3. **查看訊息**：訪問 `GET /demo/messages`
4. **處理訊息**：使用 `POST /demo/process/{message_id}`
5. **查看統計**：訪問 `GET /demo/stats`

## 📊 API 端點總覽

| 端點 | 方法 | 說明 |
|------|------|------|
| `/demo/messages` | GET | 獲取所有訊息 |
| `/demo/messages/unprocessed` | GET | 獲取未處理訊息 |
| `/demo/process/{id}` | POST | 處理指定訊息 |
| `/demo/batch-process` | POST | 批次處理所有未處理訊息 |
| `/demo/stats` | GET | 獲取統計資料 |
| `/demo/add-message` | POST | 新增訊息 |
| `/demo/contacts` | GET | 獲取聯絡人資料 |
| `/demo/user-profile` | GET | 獲取用戶設定檔 |

## 💡 注意事項

1. **時間格式**：統一使用 ISO 8601 格式 (`YYYY-MM-DDTHH:mm:ss`)
2. **編碼**：所有檔案使用 UTF-8 編碼
3. **ID 唯一性**：訊息 ID 必須唯一且遞增
4. **備份**：建議定期備份 JSON 檔案
5. **並發**：避免同時修改同一個 JSON 檔案 
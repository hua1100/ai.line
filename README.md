# AI Messenger Agent – LangChain 版

## 0. 專案簡介
本專案透過 **LangChain Agent + OpenAI Function-Calling**，實作一組可編輯 System Prompt 的通訊訊息助手。核心功能包含：

1. 自動分類訊息 (`classify_tool`)
2. 設定聯絡人優先級 (`priority_tool`)
3. 決定是否自動封存 (`archive_tool`)
4. 需要時產生回覆草稿 (`draft_reply_tool`)
5. （可選）依多因子排序對話 (`sort_tool`)

使用者可自訂 Prompt 與 Tone Profile，隨時調整標記與語調策略。

---

## 1. 系統架構
flowchart TD
    FE[前端 React / Flutter]
    WS[WebSocket Gateway]
    MQ[Message Queue (Kafka/Redis)]
    AGENT[LangChain Agent Service]
    TOOLS["Toolbox | classify / priority / archive / draft_reply / sort"]
    DB[(Postgres + VectorDB)]
    NOTI[Notification Service]

    FE -- 新訊息 --> WS --> MQ --> AGENT
    AGENT --> TOOLS
    TOOLS --> DB
    AGENT --> NOTI --> FE

---

## 2. 核心工具 (Tool) 介面
| 名稱 | Input | Output | 摘要 |
| ---- | ----- | ------ | ---- |
| `classify_tool` | `{ "text": str }` | `{ "category": "工作|朋友|家人|廣告" }` | 判斷訊息類別 |
| `priority_tool` | `{ "sender_id": str, "category": str }` | `{ "priority": int }` | 計算 1–5 級優先度 |
| `archive_tool` | `{ "category": str, "priority": int }` | `{ "should_archive": bool }` | 決定是否封存 |
| `draft_reply_tool` | `{ "text": str, "tone_profile": obj }` | `{ "draft": str }` | 生成回覆草稿 |
| `sort_tool`* | `{ "threads": list }` | `{ "sorted_threads": list }` | 多因子排序 (可選) |

\* MVP 可先由前端排序，待邏輯複雜再抽成 Tool。

---

## 3. 目錄結構 (建議)
```
ai_line/
├── src/
│   ├── api.py          # FastAPI 入口
│   ├── agent.py        # LangChain Agent 執行器
│   ├── toolbox.py      # 五大工具定義
│   ├── schemas.py      # Pydantic / JSON-Schema
│   ├── constants.py    # 分類常量等
│   ├── config.py       # 環境與模型設定
│   ├── prompts.py      # System Prompt 管理模組
│   └── database.py     # 資料庫連接與操作
├── docs/
│   └── ARCHITECTURE.md # 專案架構文件
├── tests/              # pytest 測試案例
├── requirements.txt    # Python 依賴套件
├── env.example         # 範例環境變數
└── README.md           # 本文件
```

---

## 4. 快速開始
### 4.1 先決條件
- Python 3.10+
- 建立並啟用 OpenAI API Key

### 4.2 安裝依賴
```bash
pip install -r requirements.txt
```

### 4.3 設定環境變數
```bash
cp .env.example .env
# 編輯 .env，填入 OPENAI_API_KEY 等設定
```

### 4.4 啟動服務
```bash
uvicorn src.api:app --reload
```
啟動後，`POST /organize` 接收 JSON：
```json
{
  "text": "今晚一起去看電影《沙丘2》好嗎？",
  "sender_id": "u123",
  "tone_profile": {
    "language": "zh-tw",
    "style": "極簡",
    "signature": "– Pete"
  }
}
```
將回傳
```json
{
  "category": "朋友",
  "tags": ["電影", "沙丘2", "邀約"],
  "priority": 2,
  "should_archive": false,
  "draft": "可以啊，幾點開場？"
}
```

---

## 5. 測試
```bash
pytest -q
```
測試覆蓋：
- 工具輸入輸出格式驗證
- Agent 端到端 JSON 成功率 ≥ 95%

---

## 6. 部署建議
1. Dockerfile + GitHub Actions 建置映像並推到 GHCR/ECR。
2. K8s 部署：設定 HPA 以 CPU 及延遲自動伸縮。
3. Prometheus + Grafana 監控延遲、token 用量與錯誤率。

---

## 7. Demo 模式

專案提供完整的 Demo 模式，使用 JSON 檔案儲存，無需資料庫設定。

### 快速開始 Demo
```bash
# 1. 建立範例資料
python create_sample_data.py

# 2. 啟動伺服器
./start.sh

# 3. 訪問 Demo API
curl http://localhost:8000/demo/messages
```

### Demo API 端點
- `GET /demo/messages` - 查看所有訊息
- `POST /demo/process/{id}` - 處理指定訊息
- `POST /demo/batch-process` - 批次處理
- `GET /demo/stats` - 查看統計

詳細格式請參考：`docs/JSON_DATA_FORMAT.md`

---

## 8. TODO
- [ ] 向量資料庫整合 (Qdrant) 提供相似對話檢索
- [ ] 前端 Prompt 編輯器 UI
- [ ] 自訂多語氣 Tone Profile 測試集
- [ ] Edge 模式：本地分類模型替換 `classify_tool` 

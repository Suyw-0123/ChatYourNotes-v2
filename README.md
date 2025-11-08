# ChatYourNotes Platform

ChatYourNotes 將文件上傳、OCR/摘要、向量檢索與 LLM 問答串成一條處理流水線。專案採 React + Flask + MySQL + ChromaDB 架構，由 Docker Compose 協調各服務，也能透過 uv 在本機建立 Python 環境。

## 系統概觀

```text
使用者上傳 PDF → Flask 後端：
 1. 以 pypdf 擷取文字
 2. 呼叫 Gemini (gemini-2.5-flash) 產生摘要
 3. 切分 chunk 並寫入 Chroma 向量資料庫
 4. 儲存摘要/索引路徑到 MySQL

使用者提問 → Flask 後端：
 1. 依文件或全域檢索相關 chunk
 2. 將上下文與問題送給 Gemini 取得 Markdown 回覆
 3. 回傳回答與命中片段

React 前端：
 - 檔案上傳管理
 - 文件列表與摘要預覽
 - Markdown 問答面板
```

## 目錄結構

```text
ChatYourNotes/
  backend/
    app/
      api/               # Flask Blueprint REST API
      services/          # OCR、摘要、向量、QA 等服務
      models.py          # SQLAlchemy models
      config.py          # 設定與資料夾管理
      extensions.py      # db 等擴充元件
    main.py              # WSGI 入口
    Dockerfile
    pyproject.toml       # Poetry/uv 使用的 metadata
    requirements.txt     # pip 相容需求
    .env.example         # 後端環境樣板
  frontend/
    src/
      components/
      services/
      styles.css
    Dockerfile
    package.json
    .env.example
  data/                  # PDF、OCR 結果、Chroma 向量儲存
  docker-compose.yml
  README.md
```

## 先決條件

- Docker Desktop 或相容 Docker Engine
- Node.js 18+（若要本機開發前端）
- Python 3.11（若使用 uv）
- Google Gemini API Key（寫入 `backend/.env`）

## 快速啟動（Docker Compose）

1. 建立後端環境檔：

   ```powershell
   Copy-Item backend/.env.example backend/.env
   ```

   填入 `GEMINI_API_KEY` 以及必要的 MySQL 資訊。資料目錄預設為專案下的 `data/`。

2. 建立並啟動服務：

   ```powershell
   docker compose up --build
   ```

3. 驗證服務是否運作：

   - 前端：<http://localhost:5173>
   - 後端 API：<http://localhost:8000/api>
   - MySQL：`localhost:3306`（帳號密碼見 `docker-compose.yml` / `backend/.env`）

若要停止服務：`docker compose down`

## 後端本機開發工作流程

```powershell
uv venv --python 3.11
.\.venv\Scripts\activate
uv pip install -r backend/requirements.txt
python -m unittest discover -s backend/tests
uv run python backend/main.py
```

資料與模型會存放在 `data/` 目錄，可於 `.env` 調整。

## 前端開發指令

```powershell
cd frontend
npm install
npm run dev      # 開啟 Vite 開發伺服器（預設 http://localhost:5173）

```

前端問答面板使用 Markdown 呈現 LLM 輸出，支援表格、code block 等 GFM 語法。

## API 摘要

| Method | Path                        | 說明                                       |
| ------ | --------------------------- | ------------------------------------------ |
| POST   | `/api/documents`            | 上傳 PDF（`multipart/form-data`，欄位 `file`）|
| GET    | `/api/documents`            | 取得所有文件列表與摘要預覽                 |
| DELETE | `/api/documents/<doc_id>`   | 移除文件、向量與相關檔案                   |
| POST   | `/api/qa`                   | `{"question": "...", "document_id": "optional", "top_k": 3}` |

後端回覆問答結果包含 LLM Markdown 回應與檢索片段。

## 測試與建置

- 後端單元測試：`python -m unittest discover -s backend/tests`
- 前端建置：`cd frontend && npm run build`
- Docker 重建特定服務：`docker compose build backend`、`docker compose build frontend`

## 常見問題

- **LLM 呼叫報錯**：確認 `backend/.env` 的 `GEMINI_API_KEY` 仍有效，並確保 Docker 容器已重新建立 (`docker compose up -d --force-recreate backend`).
- **MySQL 連線失敗**：檢查 Docker 是否啟動，並確認 `backend/.env` 的連線設定等同於 `docker-compose.yml`。
- **向量或摘要資料缺失**：檢查 `data/` 目錄是否存在對應子資料夾；後端啟動時會自動建立。

---

以上文件確保新成員依 README 操作即可啟動整套系統並進行文件上傳／問答測試。如有更多需求，可在 `todo.md` 添加後續工作項目。
2. Add pytest + requests integration tests

#  RAG 知識庫問答系統

完整的 RAG（檢索增強生成）系統，支持動態文檔上傳、本地 LLM 推理和現代化 Web UI。

[快速開始](#-快速開始)  [功能特性](#-功能特性)  [部署指南](./DEPLOYMENT_GUIDE.md)

##  功能特性

-  動態知識庫 - 上傳文檔自動構建知識庫
-  本地 LLM - 使用開源模型，完全隱私
-  智能檢索 - 向量相似度的快速文檔檢索  
-  RAG 對比 - 並排展示基於知識庫和不基於的回答
-  現代化 UI - 響應式設計
-  獨立可執行 - Windows EXE 無需 Python
-  完全隱私 - 所有數據保留在本地

##  快速開始

### Windows EXE (推薦)

\\\ash
# 1. 下載 EXE - GitHub Releases
# 2. 準備 LLM 模型到 models/model.gguf (可選)
# 3. 運行 rag_qa_app.exe
# 4. 訪問 http://127.0.0.1:8000
\\\

### Python 開發環境

\\\ash
git clone https://github.com/yantinglin1991/rag-qa-app.git
cd rag-qa-app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python launcher.py
\\\

##  系統架構

文檔上傳  分塊  向量化  存儲知識庫  用戶提問  向量檢索  LLM推理  返回結果

##  推薦模型

- Mistral-7B-Instruct (4.2GB)
- Llama-2-7B-Chat (3.8GB)  
- Neural-Chat-7B (4.1GB)

下載地址：https://huggingface.co/TheBloke

##  詳細文檔

- [部署指南](./DEPLOYMENT_GUIDE.md) - 完整的安裝和配置說明
- [API 文檔](./DEPLOYMENT_GUIDE.md#-api-文檔) - 所有 API 端點

##  故障排除

見 [DEPLOYMENT_GUIDE.md#-故障排除](./DEPLOYMENT_GUIDE.md#-故障排除)

##  許可證

MIT License

##  聯繫方式

- Issues: https://github.com/yantinglin1991/rag-qa-app/issues
- Discussions: https://github.com/yantinglin1991/rag-qa-app/discussions

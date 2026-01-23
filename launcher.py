from app.main import app
import uvicorn
import threading
import time
import webbrowser
import sys

def open_browser():
    """延遲打開瀏覽器，確保服務器已啟動"""
    time.sleep(2)  # 等待服務器啟動
    try:
        webbrowser.open('http://127.0.0.1:8000')
    except Exception as e:
        print(f"無法自動打開瀏覽器: {e}")
        print("請手動訪問: http://127.0.0.1:8000")

if __name__ == "__main__":
    # 如果是 PyInstaller 打包的 EXE，啟動瀏覽器線程
    if getattr(sys, 'frozen', False):
        print("\n" + "="*60)
        print("  RAG 知識庫問答系統 - 啟動中...")
        print("="*60 + "\n")
        
        # 在後臺線程中打開瀏覽器
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
    
    # 啟動 Uvicorn 服務器
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )

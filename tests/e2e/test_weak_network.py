import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_weak_network_retry_flow():
    """模擬真實用戶打開瀏覽器，測試弱網環境下的 UI 容錯與重試流程。"""
    # 初始化 Chrome 瀏覽器驅動
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # 若不想看到瀏覽器彈出，可取消註解這行
    driver = webdriver.Chrome(options=options)
    
    try:
        # 動態取得本地 index.html 的絕對路徑，不依賴 Live Server
        html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/frontend/index.html'))
        driver.get(f"file://{html_path}")
        
        # 1. 驗證行情 WebSocket 連線成功 (等待 "USD" 字樣出現)
        wait = WebDriverWait(driver, 5)
        wait.until(EC.text_to_be_present_in_element((By.ID, "price-display"), "USD"))
        
        # 2. 自動勾選「弱網模擬」
        driver.find_element(By.ID, "weak-net-toggle").click()
        
        # 3. 點擊「確認入金」
        driver.find_element(By.ID, "deposit-btn").click()
        
        # 4. 處理 20% 丟包隨機性與 3 秒延遲
        # 腳本會每秒檢查一次，如果出現藍色重試按鈕就點擊；如果直接成功就跳出迴圈
        for _ in range(10):
            retry_btn = driver.find_element(By.ID, "retry-btn")
            if retry_btn.is_displayed():
                retry_btn.click() # 點擊重試
                break
            
            logs_text = driver.find_element(By.ID, "logs").text
            if "入金成功" in logs_text:
                break
            time.sleep(1)
            
        # 5. 斷言最終結果：日誌中必定要出現「入金成功」的字樣
        wait.until(EC.text_to_be_present_in_element((By.ID, "logs"), "入金成功"))
        final_logs = driver.find_element(By.ID, "logs").text
        assert "入金成功" in final_logs
        assert "最新餘額" in final_logs
        
    finally:
        # 測試結束，關閉瀏覽器
        driver.quit()

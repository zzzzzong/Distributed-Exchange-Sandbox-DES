import uuid
import pytest
import requests

BASE_URL = "http://localhost:8000"

# 定義 10 組資料驅動測資 (Data-Driven Test Cases)
# 格式: (user_id, amount, currency, 預期HTTP狀態碼, 預期業務成功與否, 預期錯誤關鍵字)
DEPOSIT_TEST_DATA = [
    # --- 1. 正常授權路徑 (Happy Path) ---
    ("user123", 100.0, "USD", 200, True, ""),
    ("user123", 0.01, "USD", 200, True, ""),        # 極小額入金測試
    
    # --- 2. 邊界值測試 (Boundary Value Analysis) ---
    ("user123", 1000.0, "USD", 200, True, ""),      # 剛好踩在每日上限邊界 (應通過)
    ("user123", 1000.01, "USD", 200, False, "Exceeded daily limit"), # 剛好超過邊界 0.01 (應攔截)
    ("user123", 1500.0, "USD", 200, False, "Exceeded daily limit"),  # 大幅超過每日上限 (應攔截)

    # --- 3. 未知用戶預設額度測試 (Fallback Limits) ---
    ("unknown_user", 400.0, "USD", 200, True, ""),  # 未知用戶套用預設額度 500 (應通過)
    ("unknown_user", 600.0, "USD", 200, False, "Exceeded daily limit"), # 未知用戶大於預設額度 500 (應攔截)

    # --- 4. 異常負數邏輯測試 (Negative Value Edge Case) ---
    # 註: 目前的 MVP 系統中 BaseModel 僅定義 float，未阻擋負數。
    # 這裡預期它會通過合規(因為 -50 < 1000)，藉此突顯後續需增加 Pydantic 驗證的需求。
    ("user123", -50.0, "USD", 200, True, ""), 

    # --- 5. API 框架輸入型別驗證 (FastAPI/Pydantic Validation) ---
    ("user123", "not_a_number", "USD", 422, None, ""), # 故意傳入字串金額，預期 422 Unprocessable Entity
    ("user123", 100.0, None, 422, None, ""),           # 故意遺漏必填的 currency，預期 422 Unprocessable Entity
]

@pytest.mark.parametrize(
    "user_id, amount, currency, expected_status, expected_success, expected_err_keyword", 
    DEPOSIT_TEST_DATA
)
def test_fiat_deposit_data_driven(user_id, amount, currency, expected_status, expected_success, expected_err_keyword):
    """使用資料驅動模式，對 API Gateway 進行全方位的輸入邊界與合規邏輯轟炸。"""
    
    # 動態組裝 Payload，若值為 None 則刻意不在 JSON 中傳遞以測試遺漏欄位
    payload = {"user_id": user_id, "amount": amount}
    if currency is not None:
        payload["currency"] = currency

    # 確保每次發送的都是獨立的全新交易
    headers = {"Idempotency-Key": f"idemp-ddt-{uuid.uuid4()}"}
    
    # 發送 HTTP POST 請求
    response = requests.post(f"{BASE_URL}/fiat/deposit", json=payload, headers=headers)
    
    # 1. 斷言 HTTP 狀態碼
    assert response.status_code == expected_status
    
    # 2. 針對狀態碼 200 的業務邏輯進行深度斷言
    if expected_status == 200:
        data = response.json()
        assert data["success"] is expected_success
        
        if expected_success:
            # 成功時，必須回傳交易序號與新餘額
            assert "transaction_id" in data
            assert "new_balance" in data
        else:
            # 失敗時，拒絕原因必須包含我們預期的關鍵字
            assert expected_err_keyword in data["reason"]

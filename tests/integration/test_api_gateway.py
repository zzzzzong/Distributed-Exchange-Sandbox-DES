import uuid
import requests

BASE_URL = "http://localhost:8000"

def test_normal_fiat_deposit():
    """測試正常法幣入金流程，預期成功並回傳新餘額。"""
    payload = {
        "user_id": "user123",
        "amount": 100.0,
        "currency": "USD"
    }
    # 產生獨一無二的 Idempotency-Key
    headers = {"Idempotency-Key": f"idemp-{uuid.uuid4()}"}
    
    response = requests.post(f"{BASE_URL}/fiat/deposit", json=payload, headers=headers)
    
    # 斷言 HTTP 狀態碼與 JSON 回傳值
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "transaction_id" in data
    assert "new_balance" in data

def test_compliance_limit_block():
    """測試合規邊界值，當金額大於 1000 時必須被拒絕。"""
    payload = {
        "user_id": "user123",
        "amount": 1500.0,  # 故意超過 $1000 上限
        "currency": "USD"
    }
    headers = {"Idempotency-Key": f"idemp-{uuid.uuid4()}"}
    
    response = requests.post(f"{BASE_URL}/fiat/deposit", json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "Compliance check failed" in data["reason"]

import uuid
import requests

BASE_URL = "http://localhost:8000"

def test_idempotency_prevents_double_charge():
    """測試連續發送相同 Idempotency-Key 時，系統應命中緩存且防止重複記帳。"""
    payload = {
        "user_id": "user123",
        "amount": 50.0,
        "currency": "USD"
    }
    # 固定住這個 Key 模擬弱網下的 Retry
    fixed_idem_key = f"idemp-retry-{uuid.uuid4()}"
    headers = {"Idempotency-Key": fixed_idem_key}

    # 第一次請求
    resp1 = requests.post(f"{BASE_URL}/fiat/deposit", json=payload, headers=headers)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["success"] is True
    tx_id_1 = data1["transaction_id"]

    # 第二次請求 (模擬使用者點擊重試)
    resp2 = requests.post(f"{BASE_URL}/fiat/deposit", json=payload, headers=headers)
    assert resp2.status_code == 200
    data2 = resp2.json()

    # 斷言第二次回傳的交易序號必須與第一次完全相同 (命中快取)
    assert data2["success"] is True
    assert data2["transaction_id"] == tx_id_1

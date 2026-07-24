import http from 'k6/http';
import { check, sleep } from 'k6';

// 設定壓測選項
export const options = {
    vus: 100,             // 100 個虛擬並發用戶
    duration: '15s',      // 持續轟炸 15 秒
};

export default function () {
    const url = 'http://localhost:8000/fiat/deposit';
    
    // k6 內建變數，確保每個併發請求都有獨立的 Idempotency-Key
    const idemKey = `idemp-k6-${__VU}-${__ITER}-${Math.random()}`;
    
    const payload = JSON.stringify({
        user_id: 'user123',
        amount: 1.0,      // 小額壓測
        currency: 'USD',
    });

    const params = {
        headers: {
            'Content-Type': 'application/json',
            'Idempotency-Key': idemKey,
        },
    };

    // 發送 POST 請求
    const res = http.post(url, payload, params);

    // 斷言驗證 (k6 寫法)
    check(res, {
        'is status 200': (r) => r.status === 200,
        'has correct response structure': (r) => {
            const body = JSON.parse(r.body);
            return body.success === true || body.success === false;
        }
    });
    
    // 每個虛擬用戶請求間稍微等待，避免把本機網卡塞爆
    sleep(0.1);
}

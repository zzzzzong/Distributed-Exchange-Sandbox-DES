"""WebSocket Market Data Service.

作為 WebSocket Client 抓取真實交易所實時價格，並作為 WebSocket Server 轉發給前端。
"""

import asyncio
import json
import logging
import websockets

EXTERNAL_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"

async def broadcast_price(websocket: websockets.WebSocketServerProtocol) -> None:
  """將來自外部交易所的行情數據廣播給連接到本沙盒的前端。"""
  logging.info("Client connected from %s", websocket.remote_address)
  
  try:
    async with websockets.connect(EXTERNAL_WS_URL) as external_ws:
      logging.info("Connected to external Exchange WebSocket server.")
      
      while True:
        raw_msg = await external_ws.recv()
        trade_data = json.loads(raw_msg)
        
        # 'p' 在協議中代表最新成交價 (Price)
        live_price = float(trade_data.get("p", 0.0))
        
        payload = json.dumps({
            "symbol": "BTCUSD", 
            "price": round(live_price, 2)
        })
        await websocket.send(payload)
        
  except websockets.exceptions.ConnectionClosed:
    logging.info("Client disconnected.")
  except Exception as e:
    logging.error("Error in market data forwarder: %s", str(e))

async def main() -> None:
  logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
  async with websockets.serve(broadcast_price, "localhost", 8765):
    logging.info("[Market Data Svc] Listening on ws://localhost:8765...")
    await asyncio.Future()

if __name__ == "__main__":
  asyncio.run(main())

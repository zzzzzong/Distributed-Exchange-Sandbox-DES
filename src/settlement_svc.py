"""gRPC Settlement Service.

負責使用者帳本餘額的記賬與結算處理。
"""

from concurrent import futures
import logging
import os
import sys

import grpc

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import exchange_pb2
import exchange_pb2_grpc

BALANCES = {
    "user123": 150.0,  # 預設擁有 $150 USD
}

class SettlementService(exchange_pb2_grpc.SettlementServiceServicer):
  """實現 exchange.proto 中定義的 SettlementService 介面。"""

  def ProcessSettlement(
      self,
      request: exchange_pb2.SettlementRequest,
      context: grpc.ServicerContext
  ) -> exchange_pb2.SettlementResponse:
    """處理交易入金結算並更新餘額。"""
    user_id = request.user_id
    amount = request.amount
    currency = request.currency
    
    logging.info("Executing settlement for %s: +%s %s", user_id, amount, currency)
    
    current_bal = BALANCES.get(user_id, 0.0)
    new_bal = current_bal + amount
    BALANCES[user_id] = new_bal
    
    logging.info("Ledger updated for %s: %s -> %s", user_id, current_bal, new_bal)
    
    return exchange_pb2.SettlementResponse(
        success=True,
        transaction_id=request.transaction_id,
        current_balance=new_bal
    )

def serve() -> None:
  """啟動 gRPC 伺服器。"""
  logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
  exchange_pb2_grpc.add_SettlementServiceServicer_to_server(SettlementService(), server)
  server.add_insecure_port("[::]:50052")
  logging.info("[Settlement Svc] gRPC Server running on port 50052...")
  server.start()
  server.wait_for_termination()

if __name__ == "__main__":
  serve()

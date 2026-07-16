"""gRPC Compliance Service.

負責法幣入金流程中的 KYC 與每日最大充值額度校驗。
"""

from concurrent import futures
import logging
import os
import sys

import grpc

# 確保能正確載入生成的 proto 代碼
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import exchange_pb2
import exchange_pb2_grpc

USER_LIMITS = {
    "user123": 1000.0,  # 每日最大充值 $1000 USD
}

class ComplianceService(exchange_pb2_grpc.ComplianceServiceServicer):
  """實現 exchange.proto 中定義的 ComplianceService 介面。"""

  def CheckDepositLimit(
      self,
      request: exchange_pb2.ComplianceRequest,
      context: grpc.ServicerContext
  ) -> exchange_pb2.ComplianceResponse:
    """校驗使用者充值金額是否在限制額度內。"""
    user_id = request.user_id
    amount = request.amount
    currency = request.currency
    
    logging.info("Checking compliance for user %s: %s %s", user_id, amount, currency)
    
    limit = USER_LIMITS.get(user_id, 500.0)
    if amount > limit:
      return exchange_pb2.ComplianceResponse(
          approved=False,
          message=f"Compliance check failed: Exceeded daily limit of {limit} {currency}."
      )
      
    return exchange_pb2.ComplianceResponse(
        approved=True, 
        message="Compliance check passed."
    )

def serve() -> None:
  """啟動 gRPC 伺服器。"""
  logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
  exchange_pb2_grpc.add_ComplianceServiceServicer_to_server(ComplianceService(), server)
  server.add_insecure_port("[::]:50051")
  logging.info("[Compliance Svc] gRPC Server running on port 50051...")
  server.start()
  server.wait_for_termination()

if __name__ == "__main__":
  serve()

"""API Gateway Service.

系統唯一對外的 REST API 接口，負責 Idempotency-Key 校驗與微服務調用協調。
"""

import logging
import os
import sys
import uuid
from typing import Dict, Optional, Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import grpc

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import exchange_pb2
import exchange_pb2_grpc

app = FastAPI(title="Distributed Exchange Sandbox - API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 記憶體中的冪等性資料庫：儲存交易狀態與結果
IDEMPOTENCY_STORE: Dict[str, Dict[str, Any]] = {}

class DepositRequest(BaseModel):
  user_id: str
  amount: float
  currency: str

@app.post("/fiat/deposit")
async def deposit(
    request: DepositRequest, 
    idempotency_key: Optional[str] = Header(None)
) -> Dict[str, Any]:
  """處理用戶法幣入金請求。"""
  if not idempotency_key:
    raise HTTPException(status_code=400, detail="Missing Idempotency-Key Header")
  
  if idempotency_key in IDEMPOTENCY_STORE:
    record = IDEMPOTENCY_STORE[idempotency_key]
    logging.info("Idempotency hit for key: %s. Returning cached response.", idempotency_key)
    
    if record["status"] == "PENDING":
      raise HTTPException(status_code=409, detail="Transaction in progress. Please wait.")
    return record["response"]
  
  IDEMPOTENCY_STORE[idempotency_key] = {"status": "PENDING", "response": None}
  
  try:
    # 1. 呼叫 gRPC 合規服務 (Port 50051)
    with grpc.insecure_channel("localhost:50051") as channel:
      stub = exchange_pb2_grpc.ComplianceServiceStub(channel)
      comp_resp = stub.CheckDepositLimit(
          exchange_pb2.ComplianceRequest(
              user_id=request.user_id,
              amount=request.amount,
              currency=request.currency
          )
      )
    
    if not comp_resp.approved:
      err_resp = {"success": False, "reason": comp_resp.message}
      IDEMPOTENCY_STORE[idempotency_key] = {"status": "COMPLETED", "response": err_resp}
      return err_resp
    
    # 2. 合規通過，呼叫 gRPC 結算服務 (Port 50052)
    tx_id = str(uuid.uuid4())
    with grpc.insecure_channel("localhost:50052") as channel:
      stub = exchange_pb2_grpc.SettlementServiceStub(channel)
      settle_resp = stub.ProcessSettlement(
          exchange_pb2.SettlementRequest(
              user_id=request.user_id,
              amount=request.amount,
              currency=request.currency,
              transaction_id=tx_id
          )
      )
    
    success_resp = {
        "success": True,
        "transaction_id": settle_resp.transaction_id,
        "new_balance": settle_resp.current_balance
    }
    IDEMPOTENCY_STORE[idempotency_key] = {"status": "COMPLETED", "response": success_resp}
    return success_resp
    
  except Exception as e:
    logging.error("Exception processing deposit: %s", str(e))
    IDEMPOTENCY_STORE.pop(idempotency_key, None)
    raise HTTPException(status_code=500, detail=f"Internal Service Error: {str(e)}")

@app.get("/health")
def health() -> Dict[str, str]:
  return {"status": "OK"}

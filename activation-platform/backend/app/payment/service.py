from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime


class PaymentService:
  """支付服务（迁移自 services/payment_service.py）
  最小可用实现，便于 API 启动与联调；后续可替换为基于支付提供商的真实实现。
  """

  def __init__(self, db: Session):
    self.db = db

  def get_supported_payment_methods(self) -> List[str]:
    return ["mock"]

  def create_payment(self, request: Any, client_ip: str) -> Dict[str, Any]:
    amount = float(getattr(request, "amount", 0) or getattr(request, "price", 0) or 0)
    currency = getattr(request, "currency", "CNY")
    return {
      "success": True,
      "payment_id": "PAY_TEST_0001",
      "payment_url": None,
      "qr_code": None,
      "amount": amount,
      "currency": currency,
      "message": "mock payment created"
    }

  def get_payment_status(self, payment_id: str) -> Any:
    class Payment:
      def __init__(self):
        self.id = 1
        self.payment_id = payment_id
        self.activation_code_id = None
        self.amount = 0.0
        self.currency = "CNY"
        self.method = "mock"
        self.status = "success"
        self.third_party_order_id = None
        self.paid_at = datetime.utcnow()
        self.created_at = datetime.utcnow()
    return Payment()

  def handle_payment_callback(self, callback: Any) -> Dict[str, Any]:
    return {"success": True, "message": "callback processed"}

  def create_payment_with_activation_code(self, **kwargs) -> Dict[str, Any]:
    return {
      "success": True,
      "payment_id": "PAY_TEST_0002",
      "activation_code_id": 1,
      "activation_code": "ACTTESTCODE",
      "payment_url": None,
      "qr_code": None,
      "amount": float(kwargs.get("price", 0)),
      "currency": "CNY",
      "product_name": kwargs.get("product_name") or "TEST"
    }

  def process_payment_success(self, payment_id: str) -> Dict[str, Any]:
    return {
      "success": True,
      "payment_id": payment_id,
      "message": "payment success",
      "paid_at": datetime.utcnow(),
    }

  def refund_payment(self, payment_id: str, reason: str) -> Dict[str, Any]:
    return {"success": True, "message": f"refunded: {reason}"}

  def get_payment_statistics(self) -> Dict[str, Any]:
    return {
      "total_amount": 0.0,
      "total_orders": 0,
      "success_orders": 0,
      "failed_orders": 0,
      "method_stats": {},
      "daily_stats": {}
    }



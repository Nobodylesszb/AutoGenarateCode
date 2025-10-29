from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from .manager import PaymentManager
from . import PaymentMethod


class PaymentService:
  """支付服务：委托 PaymentManager，支持 mock、pingxx 等多渠道"""

  def __init__(self, db: Session):
    self.db = db
    self.manager = PaymentManager(db)

  def get_supported_payment_methods(self) -> List[str]:
    return [m.value for m in self.manager.get_supported_methods()]

  def create_payment(self, request: Any, client_ip: str) -> Dict[str, Any]:
    amount = float(getattr(request, "amount", 0) or getattr(request, "price", 0) or 0)
    currency = getattr(request, "currency", "CNY")
    method_str = getattr(request, "method", None)
    method = self.manager.convert_payment_method(method_str or "mock")
    description = getattr(request, "product_name", None) or "Activation"

    result = self.manager.create_payment(method, amount, description, client_ip)
    return {
      "success": result.success,
      "payment_id": result.payment_id,
      "payment_url": result.payment_url,
      "qr_code": result.qr_code,
      "amount": result.amount or amount,
      "currency": result.currency or currency,
      "message": result.message,
    }

  def get_payment_status(self, payment_id: str):
    # 这里简化返回结构，实际可查询数据库记录
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
    # 回调处理留作后续：结合签名验签与状态落库
    return {"success": True, "message": "callback processed"}

  def create_payment_with_activation_code(self, **kwargs) -> Dict[str, Any]:
    method = self.manager.convert_payment_method(kwargs.get("payment_method", "mock"))
    amount = float(kwargs.get("price", 0))
    description = kwargs.get("product_name") or "Activation"
    client_ip = kwargs.get("client_ip", "127.0.0.1")
    result = self.manager.create_payment(method, amount, description, client_ip)
    return {
      "success": result.success,
      "payment_id": result.payment_id,
      "activation_code_id": kwargs.get("activation_code_id", 1),
      "activation_code": kwargs.get("activation_code", ""),
      "payment_url": result.payment_url,
      "qr_code": result.qr_code,
      "amount": result.amount or amount,
      "currency": result.currency or "CNY",
      "product_name": description
    }

  def process_payment_success(self, payment_id: str) -> Dict[str, Any]:
    return {
      "success": True,
      "payment_id": payment_id,
      "message": "payment success",
      "paid_at": datetime.utcnow(),
    }

  def refund_payment(self, payment_id: str, reason: str) -> Dict[str, Any]:
    # 默认使用 Ping++ 渠道退款：实际应记录支付方式
    result = self.manager.refund_payment(PaymentMethod.PINGXX, payment_id, 0.0, reason)
    return {"success": result.success, "message": result.message}

  def get_payment_statistics(self) -> Dict[str, Any]:
    return self.manager.get_payment_statistics()



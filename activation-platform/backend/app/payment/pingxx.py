"""
Ping++ 支付提供商
参考文档: https://www.pingxx.com/docs/downloads.html
"""

from typing import Dict, Any

from . import PaymentProvider, PaymentResult, PaymentConfig


class PingxxPaymentProvider(PaymentProvider):
  """Ping++ 支付提供商实现
  需要配置: api_key, app_id, private_key（或路径）
  """

  def __init__(self, config: PaymentConfig):
    super().__init__(config)
    try:
      import pingpp  # type: ignore
      self._pingpp = pingpp
    except Exception as e:
      raise RuntimeError("缺少 pingpp 依赖，请在后端安装 pingpp SDK") from e

    # 基础配置
    self._pingpp.api_key = (config.api_key or "").strip()
    if not self._pingpp.api_key:
      raise ValueError("未配置 Ping++ api_key")

    # 设置私钥（可以是字符串或文件路径）
    if config.private_key and "BEGIN RSA PRIVATE KEY" in config.private_key:
      self._pingpp.private_key = config.private_key
    elif config.private_key:
      # 认为是路径
      with open(config.private_key, 'r') as f:
        self._pingpp.private_key = f.read()
    else:
      raise ValueError("未配置 Ping++ private_key")

    self._app_id = (config.app_id or "").strip()
    if not self._app_id:
      raise ValueError("未配置 Ping++ app_id")

  def create_order(self, payment_id: str, amount: float, description: str,
                   client_ip: str = "127.0.0.1", **kwargs) -> PaymentResult:
    try:
      channel = kwargs.get("channel", "alipay")  # 由上层传入: alipay, wx, upacp 等
      order_no = payment_id
      amount_in_fen = int(round(amount * 100))

      ch = self._pingpp.Charge.create(
        order_no=order_no,
        app={"id": self._app_id},
        amount=amount_in_fen,
        channel=channel,
        currency=self.config.extra_config.get("currency", "cny"),
        client_ip=client_ip,
        subject=description[:32] if description else "Activation",
        body=description[:128] if description else "Activation Code Payment",
        extra=kwargs.get("extra") or {}
      )

      payment_url = ch.get("credential")
      return PaymentResult(
        success=True,
        payment_id=payment_id,
        payment_url=payment_url,
        amount=amount,
        currency=self.config.extra_config.get("currency", "CNY"),
        message="Ping++ 订单创建成功",
        extra_data={"charge": ch}
      )

    except Exception as e:
      self.logger.error(f"Ping++ 创建订单失败: {str(e)}")
      return PaymentResult(success=False, payment_id=payment_id, message=str(e))

  def verify_callback(self, callback_data: Dict[str, Any]) -> bool:
    # Ping++ 官方建议通过签名头验证，这里预留，实际应校验 X-Pingplusplus-Signature
    try:
      # 开发阶段可直接返回 True，生产应严格验签
      return True
    except Exception as e:
      self.logger.error(f"Ping++ 回调验签失败: {str(e)}")
      return False

  def query_order(self, payment_id: str) -> PaymentResult:
    try:
      ch = self._pingpp.Charge.retrieve(payment_id)
      paid = ch.get("paid") is True
      return PaymentResult(
        success=paid,
        payment_id=payment_id,
        amount=(ch.get("amount", 0) or 0) / 100.0,
        message="订单已支付" if paid else "订单未支付",
        extra_data={"charge": ch}
      )
    except Exception as e:
      return PaymentResult(success=False, payment_id=payment_id, message=str(e))

  def refund(self, payment_id: str, amount: float, reason: str = "") -> PaymentResult:
    try:
      ch = self._pingpp.Charge.retrieve(payment_id)
      refund = ch.refunds.create(amount=int(round(amount * 100)), description=reason or "退款")
      succeeded = refund.get("succeed") is True
      return PaymentResult(
        success=succeeded,
        payment_id=payment_id,
        amount=amount,
        message="退款成功" if succeeded else "退款提交成功，等待结果",
        extra_data={"refund": refund}
      )
    except Exception as e:
      return PaymentResult(success=False, payment_id=payment_id, message=str(e))



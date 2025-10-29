from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import PaymentCallback
from app.payment.service import PaymentService

router = APIRouter()

@router.post("/payment/wechat")
async def wechat_webhook(
    request: dict,
    db: Session = Depends(get_db)
):
    """微信支付Webhook"""
    service = PaymentService(db)
    
    # 构建回调对象
    callback = PaymentCallback(
        payment_id=request.get("out_trade_no"),
        third_party_order_id=request.get("transaction_id"),
        status="SUCCESS" if request.get("result_code") == "SUCCESS" else "FAILED",
        amount=float(request.get("total_fee", 0)) / 100,
        callback_data=request
    )
    
    result = service.handle_payment_callback(callback)
    
    if result["success"]:
        return {"return_code": "SUCCESS", "return_msg": "OK"}
    else:
        return {"return_code": "FAIL", "return_msg": result["message"]}

@router.post("/payment/alipay")
async def alipay_webhook(
    request: dict,
    db: Session = Depends(get_db)
):
    """支付宝支付Webhook"""
    service = PaymentService(db)
    
    # 构建回调对象
    callback = PaymentCallback(
        payment_id=request.get("out_trade_no"),
        third_party_order_id=request.get("trade_no"),
        status="SUCCESS" if request.get("trade_status") == "TRADE_SUCCESS" else "FAILED",
        amount=float(request.get("total_amount", 0)),
        callback_data=request
    )
    
    result = service.handle_payment_callback(callback)
    
    if result["success"]:
        return "success"
    else:
        return "fail"

@router.post("/payment/pingxx")
async def pingxx_webhook(
    request_obj: Request,
    db: Session = Depends(get_db)
):
    """Ping++ 支付 Webhook（需配合签名验签）"""
    service = PaymentService(db)
    headers = dict(request_obj.headers)
    signature = headers.get("X-Pingplusplus-Signature") or headers.get("x-pingplusplus-signature")
    body = await request_obj.body()
    # 这里将原始数据传入回调处理，验签逻辑在 provider 中进一步实现
    callback = {
        "signature": signature,
        "body": body.decode("utf-8", errors="ignore"),
        "headers": headers
    }
    result = service.handle_payment_callback(callback)
    if result.get("success"):
        return {"status": "ok"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("message") or "invalid signature")

@router.post("/activation/notify")
async def activation_notify(
    request: dict,
    db: Session = Depends(get_db)
):
    """激活码使用通知Webhook"""
    # 这里可以添加激活码使用后的通知逻辑
    # 比如发送邮件、短信、或者调用其他系统的API
    
    return {
        "success": True,
        "message": "通知发送成功"
    }

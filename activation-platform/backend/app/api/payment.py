from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    PaymentCreate, PaymentResponse, PaymentCallback,
    PaymentCreateWithProduct, PaymentSuccessResponse,
    PaymentRefundRequest, PaymentStatistics
)
from app.services.payment_service import PaymentService
from app.models import PaymentStatus

router = APIRouter()

@router.get("/methods")
async def get_supported_payment_methods(
    db: Session = Depends(get_db)
):
    """获取支持的支付方式"""
    service = PaymentService(db)
    methods = service.get_supported_payment_methods()
    return {"methods": methods}

@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    request: PaymentCreate,
    request_client: Request,
    db: Session = Depends(get_db)
):
    """创建支付订单"""
    # 获取客户端IP
    client_ip = request_client.client.host
    
    service = PaymentService(db)
    result = service.create_payment(request, client_ip)
    
    if result["success"]:
        # 获取支付记录
        payment = service.get_payment_status(result["payment_id"])
        return PaymentResponse(
            id=payment.id,
            payment_id=payment.payment_id,
            activation_code_id=payment.activation_code_id,
            amount=payment.amount,
            currency=payment.currency,
            method=payment.method,
            status=payment.status,
            third_party_order_id=payment.third_party_order_id,
            paid_at=payment.paid_at,
            created_at=payment.created_at,
            payment_url=result.get("payment_url"),
            qr_code=result.get("qr_code")
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

@router.get("/status/{payment_id}", response_model=PaymentResponse)
async def get_payment_status(
    payment_id: str,
    db: Session = Depends(get_db)
):
    """获取支付状态"""
    service = PaymentService(db)
    payment = service.get_payment_status(payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支付记录不存在"
        )
    
    return PaymentResponse(
        id=payment.id,
        payment_id=payment.payment_id,
        activation_code_id=payment.activation_code_id,
        amount=payment.amount,
        currency=payment.currency,
        method=payment.method,
        status=payment.status,
        third_party_order_id=payment.third_party_order_id,
        paid_at=payment.paid_at,
        created_at=payment.created_at
    )

@router.post("/callback/wechat")
async def wechat_payment_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """微信支付回调"""
    # 获取回调数据
    callback_data = await request.form()
    callback_dict = dict(callback_data)
    
    service = PaymentService(db)
    
    # 构建回调对象
    callback = PaymentCallback(
        payment_id=callback_dict.get("out_trade_no"),
        third_party_order_id=callback_dict.get("transaction_id"),
        status="SUCCESS" if callback_dict.get("result_code") == "SUCCESS" else "FAILED",
        amount=float(callback_dict.get("total_fee", 0)) / 100,  # 转换为元
        callback_data=callback_dict
    )
    
    result = service.handle_payment_callback(callback)
    
    if result["success"]:
        return {"return_code": "SUCCESS", "return_msg": "OK"}
    else:
        return {"return_code": "FAIL", "return_msg": result["message"]}

@router.post("/callback/alipay")
async def alipay_payment_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """支付宝支付回调"""
    # 获取回调数据
    callback_data = await request.form()
    callback_dict = dict(callback_data)
    
    service = PaymentService(db)
    
    # 构建回调对象
    callback = PaymentCallback(
        payment_id=callback_dict.get("out_trade_no"),
        third_party_order_id=callback_dict.get("trade_no"),
        status="SUCCESS" if callback_dict.get("trade_status") == "TRADE_SUCCESS" else "FAILED",
        amount=float(callback_dict.get("total_amount", 0)),
        callback_data=callback_dict
    )
    
    result = service.handle_payment_callback(callback)
    
    if result["success"]:
        return "success"
    else:
        return "fail"

@router.post("/create-with-product")
async def create_payment_with_product(
    request: PaymentCreateWithProduct,
    request_client: Request,
    db: Session = Depends(get_db)
):
    """创建支付并生成激活码"""
    # 获取客户端IP
    client_ip = request_client.client.host
    
    service = PaymentService(db)
    result = service.create_payment_with_activation_code(
        product_id=request.product_id,
        product_name=request.product_name,
        price=float(request.price),
        payment_method=request.method.value,
        client_ip=client_ip,
        max_activations=request.max_activations
    )
    
    if result["success"]:
        return {
            "success": True,
            "payment_id": result["payment_id"],
            "activation_code_id": result["activation_code_id"],
            "activation_code": result["activation_code"],
            "payment_url": result.get("payment_url"),
            "qr_code": result.get("qr_code"),
            "amount": result["amount"],
            "currency": result["currency"],
            "product_name": result["product_name"]
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

@router.get("/success/{payment_id}", response_model=PaymentSuccessResponse)
async def get_payment_success_info(
    payment_id: str,
    db: Session = Depends(get_db)
):
    """获取支付成功信息"""
    service = PaymentService(db)
    result = service.process_payment_success(payment_id)
    
    if result["success"]:
        return PaymentSuccessResponse(**result)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

@router.post("/refund")
async def refund_payment(
    request: PaymentRefundRequest,
    db: Session = Depends(get_db)
):
    """退款处理"""
    service = PaymentService(db)
    result = service.refund_payment(request.payment_id, request.reason)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

@router.get("/statistics", response_model=PaymentStatistics)
async def get_payment_statistics(
    db: Session = Depends(get_db)
):
    """获取支付统计信息"""
    service = PaymentService(db)
    stats = service.get_payment_statistics()
    return PaymentStatistics(**stats)

@router.get("/list")
async def get_payment_list(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """获取支付列表"""
    from app.models import Payment
    from sqlalchemy import desc
    
    query = db.query(Payment)
    
    if status:
        query = query.filter(Payment.status == status)
    
    payments = query.order_by(desc(Payment.created_at)).offset(skip).limit(limit).all()
    
    return [
        {
            "id": payment.id,
            "payment_id": payment.payment_id,
            "activation_code_id": payment.activation_code_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "method": payment.method.value,
            "status": payment.status.value,
            "third_party_order_id": payment.third_party_order_id,
            "paid_at": payment.paid_at,
            "created_at": payment.created_at
        }
        for payment in payments
    ]

@router.post("/test/mock-payment")
async def create_mock_payment(
    request: PaymentCreateWithProduct,
    request_client: Request,
    db: Session = Depends(get_db)
):
    """创建模拟支付（用于测试）"""
    # 获取客户端IP
    client_ip = request_client.client.host
    
    service = PaymentService(db)
    result = service.create_payment_with_activation_code(
        product_id=request.product_id,
        product_name=request.product_name,
        price=float(request.price),
        payment_method="mock",  # 使用模拟支付
        client_ip=client_ip,
        max_activations=request.max_activations
    )
    
    if result["success"]:
        return {
            "success": True,
            "payment_id": result["payment_id"],
            "activation_code_id": result["activation_code_id"],
            "activation_code": result["activation_code"],
            "payment_url": result.get("payment_url"),
            "qr_code": result.get("qr_code"),
            "amount": result["amount"],
            "currency": result["currency"],
            "product_name": result["product_name"],
            "note": "这是模拟支付，用于测试"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

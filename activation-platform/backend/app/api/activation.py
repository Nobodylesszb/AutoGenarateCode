from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import platform
from app.database import get_db
from app.schemas import (
    ActivationCodeCreate, ActivationCodeResponse, ActivationCodeVerify,
    ActivationCodeVerifyResponse, PaymentCreate, PaymentResponse,
    HardwareBindingRequest, HardwareBindingResponse,
    HardwareVerificationRequest, HardwareVerificationResponse,
    HardwareUnbindRequest, HardwareFingerprintResponse,
    UnifiedActivationRequest, UnifiedActivationResponse,
    ActivationCodeUseRequest
)
from app.services.activation_service import ActivationCodeService
from app.services.payment_service import PaymentService
from app.models import ActivationCodeStatus

router = APIRouter()

# 原有的激活码接口保持不变
@router.post("/generate", response_model=List[ActivationCodeResponse])
async def generate_activation_codes(
    request: ActivationCodeCreate,
    db: Session = Depends(get_db)
):
    """生成激活码（软件激活码系统）"""
    service = ActivationCodeService(db)
    activation_codes = service.create_activation_codes(request)
    return activation_codes

@router.get("/verify/{code}", response_model=ActivationCodeVerifyResponse)
async def verify_activation_code(
    code: str,
    db: Session = Depends(get_db)
):
    """验证激活码（软件激活码系统）"""
    service = ActivationCodeService(db)
    result = service.verify_activation_code(ActivationCodeVerify(code=code))
    return ActivationCodeVerifyResponse(**result)

@router.post("/use/{code}")
async def use_activation_code(
    code: str,
    user_id: str = None,
    db: Session = Depends(get_db)
):
    """使用激活码（软件激活码系统）"""
    service = ActivationCodeService(db)
    result = service.use_activation_code(code, user_id)
    return result

@router.post("/use")
async def use_activation_code_with_details(
    request: ActivationCodeUseRequest,
    db: Session = Depends(get_db)
):
    """使用激活码（带详细信息）"""
    service = ActivationCodeService(db)
    result = service.use_activation_code(
        request.code,
        request.user_id,
        request.device_info,
        request.ip_address
    )
    return result

@router.get("/records/{code}")
async def get_activation_records(
    code: str,
    db: Session = Depends(get_db)
):
    """获取激活记录"""
    service = ActivationCodeService(db)
    result = service.get_activation_records(code)
    return result

# 硬件绑定接口保持不变
@router.post("/hardware/generate-fingerprint", response_model=HardwareFingerprintResponse)
async def generate_hardware_fingerprint():
    """生成硬件指纹"""
    from app.services.activation_service import HardwareFingerprint
    from datetime import datetime
    
    fingerprint = HardwareFingerprint.generate_hardware_fingerprint()
    device_info = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node()
    }
    
    return HardwareFingerprintResponse(
        fingerprint=fingerprint,
        device_info=device_info,
        generated_at=datetime.utcnow()
    )

@router.post("/hardware/bind", response_model=HardwareBindingResponse)
async def bind_activation_code_to_hardware(
    request: HardwareBindingRequest,
    db: Session = Depends(get_db)
):
    """将激活码绑定到硬件"""
    service = ActivationCodeService(db)
    result = service.bind_to_hardware(
        request.activation_code,
        request.hardware_fingerprint,
        request.user_id
    )
    
    return HardwareBindingResponse(
        success=result["success"],
        message=result["message"],
        binding_info=result.get("binding_info")
    )

@router.post("/hardware/verify", response_model=HardwareVerificationResponse)
async def verify_hardware_binding(
    request: HardwareVerificationRequest,
    db: Session = Depends(get_db)
):
    """验证硬件绑定"""
    service = ActivationCodeService(db)
    result = service.verify_hardware_binding(
        request.activation_code,
        request.hardware_fingerprint
    )
    
    return HardwareVerificationResponse(
        valid=result["valid"],
        message=result["message"],
        binding_info=result.get("binding_info")
    )

@router.get("/hardware/binding-info/{code}")
async def get_hardware_binding_info(
    code: str,
    db: Session = Depends(get_db)
):
    """获取硬件绑定信息"""
    service = ActivationCodeService(db)
    result = service.get_hardware_binding_info(code)
    return result

@router.post("/hardware/unbind")
async def unbind_hardware(
    request: HardwareUnbindRequest,
    db: Session = Depends(get_db)
):
    """解绑硬件（管理员功能）"""
    service = ActivationCodeService(db)
    result = service.unbind_hardware(
        request.activation_code,
        request.admin_key
    )
    return result

# 新增：统一激活码接口
@router.post("/unified/activate", response_model=UnifiedActivationResponse)
async def unified_activation(
    request: UnifiedActivationRequest,
    db: Session = Depends(get_db)
):
    """
    统一激活码接口
    根据产品类型自动选择激活码系统
    """
    service = ActivationCodeService(db)
    
    # 检查产品是否需要硬件绑定
    product_requires_hardware = request.product_type == "hardware_bound"
    
    if product_requires_hardware:
        # 使用硬件绑定系统
        if not request.hardware_fingerprint:
            raise HTTPException(
                status_code=400,
                detail="硬件绑定产品需要提供硬件指纹"
            )
        
        # 验证硬件绑定
        verify_result = service.verify_hardware_binding(
            request.activation_code,
            request.hardware_fingerprint
        )
        
        return UnifiedActivationResponse(
            success=verify_result["valid"],
            message=verify_result["message"],
            activation_type="hardware_bound",
            binding_info=verify_result.get("binding_info")
        )
    
    else:
        # 使用软件激活码系统
        verify_result = service.verify_activation_code(
            ActivationCodeVerify(code=request.activation_code)
        )
        
        return UnifiedActivationResponse(
            success=verify_result["valid"],
            message=verify_result["message"],
            activation_type="software",
            activation_code=verify_result.get("activation_code")
        )

@router.post("/unified/bind")
async def unified_bind_activation(
    request: UnifiedActivationRequest,
    db: Session = Depends(get_db)
):
    """
    统一绑定接口
    根据产品类型自动选择绑定方式
    """
    service = ActivationCodeService(db)
    
    # 检查产品是否需要硬件绑定
    product_requires_hardware = request.product_type == "hardware_bound"
    
    if product_requires_hardware:
        # 使用硬件绑定
        if not request.hardware_fingerprint:
            raise HTTPException(
                status_code=400,
                detail="硬件绑定产品需要提供硬件指纹"
            )
        
        result = service.bind_to_hardware(
            request.activation_code,
            request.hardware_fingerprint,
            request.user_id
        )
        
        return UnifiedActivationResponse(
            success=result["success"],
            message=result["message"],
            activation_type="hardware_bound",
            binding_info=result.get("binding_info")
        )
    
    else:
        # 使用软件激活码
        result = service.use_activation_code(
            request.activation_code,
            request.user_id
        )
        
        return UnifiedActivationResponse(
            success=result["success"],
            message=result["message"],
            activation_type="software",
            activation_code=result.get("activation_code")
        )

# 产品管理接口
@router.get("/products")
async def get_products(db: Session = Depends(get_db)):
    """获取产品列表"""
    # 这里可以返回产品配置，包括是否需要硬件绑定
    products = [
        {
            "product_id": "basic_software",
            "product_name": "基础软件",
            "price": 99.00,
            "requires_hardware_binding": False,
            "description": "标准软件激活码，支持批量生成"
        },
        {
            "product_id": "premium_software",
            "product_name": "高级软件",
            "price": 299.00,
            "requires_hardware_binding": True,
            "description": "硬件绑定激活码，防止盗版"
        },
        {
            "product_id": "enterprise_software",
            "product_name": "企业软件",
            "price": 999.00,
            "requires_hardware_binding": True,
            "description": "企业级软件，严格硬件绑定"
        }
    ]
    return products

@router.get("/stats")
async def get_activation_code_stats(
    product_id: str = None,
    db: Session = Depends(get_db)
):
    """获取激活码统计信息"""
    service = ActivationCodeService(db)
    stats = service.get_activation_code_stats(product_id)
    return stats

@router.get("/security-info")
async def get_activation_code_security_info(
    db: Session = Depends(get_db)
):
    """获取激活码安全信息"""
    service = ActivationCodeService(db)
    security_info = service.get_code_security_info()
    return security_info
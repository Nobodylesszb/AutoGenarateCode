#!/usr/bin/env python3
"""
激活码平台客户端SDK示例
支持软件激活码和硬件绑定两种模式
"""

import requests
import json
import platform
import hashlib
import psutil
from typing import Dict, Any, Optional
from datetime import datetime

class ActivationCodeClient:
    """激活码客户端SDK"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ActivationCodeClient/1.0'
        })
    
    def generate_hardware_fingerprint(self) -> str:
        """生成硬件指纹"""
        try:
            # 收集硬件信息
            hardware_info = {
                'cpu_count': psutil.cpu_count(),
                'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                'memory_total': psutil.virtual_memory().total,
                'platform': platform.platform(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'hostname': platform.node(),
            }
            
            # 生成指纹
            fingerprint_data = json.dumps(hardware_info, sort_keys=True)
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
            return fingerprint
            
        except Exception as e:
            print(f"生成硬件指纹失败: {e}")
            # 使用备用方案
            fallback_info = {
                'hostname': platform.node(),
                'platform': platform.platform(),
                'timestamp': str(int(datetime.now().timestamp()))
            }
            fingerprint_data = json.dumps(fallback_info, sort_keys=True)
            return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def activate_software_license(self, activation_code: str, user_id: str = None) -> Dict[str, Any]:
        """
        软件激活码激活（传统方式）
        
        Args:
            activation_code: 激活码
            user_id: 用户ID
            
        Returns:
            激活结果
        """
        try:
            # 验证激活码
            verify_url = f"{self.base_url}/api/v1/activation/verify/{activation_code}"
            verify_response = self.session.get(verify_url)
            
            if verify_response.status_code != 200:
                return {
                    "success": False,
                    "message": f"验证失败: HTTP {verify_response.status_code}"
                }
            
            verify_data = verify_response.json()
            
            if not verify_data.get("valid"):
                return {
                    "success": False,
                    "message": verify_data.get("message", "激活码无效")
                }
            
            # 使用激活码
            use_url = f"{self.base_url}/api/v1/activation/use/{activation_code}"
            use_data = {"user_id": user_id} if user_id else {}
            use_response = self.session.post(use_url, json=use_data)
            
            if use_response.status_code != 200:
                return {
                    "success": False,
                    "message": f"使用失败: HTTP {use_response.status_code}"
                }
            
            use_result = use_response.json()
            
            return {
                "success": use_result.get("success", False),
                "message": use_result.get("message", "激活完成"),
                "activation_type": "software",
                "activation_code": verify_data.get("activation_code")
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"激活失败: {str(e)}"
            }
    
    def activate_hardware_bound_license(self, activation_code: str, user_id: str = None) -> Dict[str, Any]:
        """
        硬件绑定激活码激活
        
        Args:
            activation_code: 激活码
            user_id: 用户ID
            
        Returns:
            激活结果
        """
        try:
            # 生成硬件指纹
            hardware_fingerprint = self.generate_hardware_fingerprint()
            
            # 绑定激活码到硬件
            bind_url = f"{self.base_url}/api/v1/activation/hardware/bind"
            bind_data = {
                "activation_code": activation_code,
                "hardware_fingerprint": hardware_fingerprint,
                "user_id": user_id
            }
            
            bind_response = self.session.post(bind_url, json=bind_data)
            
            if bind_response.status_code != 200:
                return {
                    "success": False,
                    "message": f"绑定失败: HTTP {bind_response.status_code}"
                }
            
            bind_result = bind_response.json()
            
            if not bind_result.get("success"):
                return {
                    "success": False,
                    "message": bind_result.get("message", "硬件绑定失败")
                }
            
            return {
                "success": True,
                "message": "硬件绑定激活成功",
                "activation_type": "hardware_bound",
                "binding_info": bind_result.get("binding_info"),
                "hardware_fingerprint": hardware_fingerprint
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"硬件绑定激活失败: {str(e)}"
            }
    
    def verify_hardware_bound_license(self, activation_code: str) -> Dict[str, Any]:
        """
        验证硬件绑定激活码
        
        Args:
            activation_code: 激活码
            
        Returns:
            验证结果
        """
        try:
            # 生成当前硬件指纹
            hardware_fingerprint = self.generate_hardware_fingerprint()
            
            # 验证硬件绑定
            verify_url = f"{self.base_url}/api/v1/activation/hardware/verify"
            verify_data = {
                "activation_code": activation_code,
                "hardware_fingerprint": hardware_fingerprint
            }
            
            verify_response = self.session.post(verify_url, json=verify_data)
            
            if verify_response.status_code != 200:
                return {
                    "valid": False,
                    "message": f"验证失败: HTTP {verify_response.status_code}"
                }
            
            verify_result = verify_response.json()
            
            return {
                "valid": verify_result.get("valid", False),
                "message": verify_result.get("message", "验证失败"),
                "binding_info": verify_result.get("binding_info")
            }
            
        except Exception as e:
            return {
                "valid": False,
                "message": f"验证失败: {str(e)}"
            }
    
    def unified_activation(self, activation_code: str, product_type: str, user_id: str = None) -> Dict[str, Any]:
        """
        统一激活接口
        
        Args:
            activation_code: 激活码
            product_type: 产品类型 ("software" 或 "hardware_bound")
            user_id: 用户ID
            
        Returns:
            激活结果
        """
        try:
            # 准备请求数据
            request_data = {
                "activation_code": activation_code,
                "product_type": product_type,
                "user_id": user_id
            }
            
            # 如果是硬件绑定产品，需要生成硬件指纹
            if product_type == "hardware_bound":
                hardware_fingerprint = self.generate_hardware_fingerprint()
                request_data["hardware_fingerprint"] = hardware_fingerprint
            
            # 调用统一激活接口
            activate_url = f"{self.base_url}/api/v1/activation/unified/activate"
            activate_response = self.session.post(activate_url, json=request_data)
            
            if activate_response.status_code != 200:
                return {
                    "success": False,
                    "message": f"激活失败: HTTP {activate_response.status_code}"
                }
            
            activate_result = activate_response.json()
            
            return {
                "success": activate_result.get("success", False),
                "message": activate_result.get("message", "激活失败"),
                "activation_type": activate_result.get("activation_type", product_type),
                "activation_code": activate_result.get("activation_code"),
                "binding_info": activate_result.get("binding_info")
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"统一激活失败: {str(e)}"
            }
    
    def get_products(self) -> Dict[str, Any]:
        """获取产品列表"""
        try:
            products_url = f"{self.base_url}/api/v1/activation/products"
            response = self.session.get(products_url)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "products": response.json()
                }
            else:
                return {
                    "success": False,
                    "message": f"获取产品列表失败: HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"获取产品列表失败: {str(e)}"
            }
    
    def get_security_info(self) -> Dict[str, Any]:
        """获取安全信息"""
        try:
            security_url = f"{self.base_url}/api/v1/activation/security-info"
            response = self.session.get(security_url)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "security_info": response.json()
                }
            else:
                return {
                    "success": False,
                    "message": f"获取安全信息失败: HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"获取安全信息失败: {str(e)}"
            }

def main():
    """示例用法"""
    print("🚀 激活码平台客户端SDK示例")
    print("=" * 50)
    
    # 创建客户端
    client = ActivationCodeClient()
    
    # 获取产品列表
    print("1. 获取产品列表:")
    products_result = client.get_products()
    if products_result["success"]:
        for product in products_result["products"]:
            print(f"   - {product['product_name']}: {product['price']}元")
            print(f"     硬件绑定: {'是' if product['requires_hardware_binding'] else '否'}")
    else:
        print(f"   ❌ {products_result['message']}")
    
    # 获取安全信息
    print("\n2. 获取安全信息:")
    security_result = client.get_security_info()
    if security_result["success"]:
        security_info = security_result["security_info"]
        print(f"   - 激活码长度: {security_info['default_length']}")
        print(f"   - 加密方法: {security_info['encryption_method']}")
        print(f"   - 硬件绑定: {'支持' if security_info['hardware_binding'] else '不支持'}")
    else:
        print(f"   ❌ {security_result['message']}")
    
    # 测试软件激活码
    print("\n3. 测试软件激活码激活:")
    software_result = client.activate_software_license("ACT1234567890ABCDEF", "test_user")
    print(f"   结果: {software_result['success']}")
    print(f"   消息: {software_result['message']}")
    
    # 测试硬件绑定激活码
    print("\n4. 测试硬件绑定激活码激活:")
    hardware_result = client.activate_hardware_bound_license("ACT1234567890ABCDEF", "test_user")
    print(f"   结果: {hardware_result['success']}")
    print(f"   消息: {hardware_result['message']}")
    if hardware_result['success']:
        print(f"   硬件指纹: {hardware_result['hardware_fingerprint'][:20]}...")
    
    # 测试统一激活接口
    print("\n5. 测试统一激活接口:")
    
    # 软件产品
    unified_software = client.unified_activation("ACT1234567890ABCDEF", "software", "test_user")
    print(f"   软件产品激活: {unified_software['success']}")
    print(f"   消息: {unified_software['message']}")
    
    # 硬件绑定产品
    unified_hardware = client.unified_activation("ACT1234567890ABCDEF", "hardware_bound", "test_user")
    print(f"   硬件绑定产品激活: {unified_hardware['success']}")
    print(f"   消息: {unified_hardware['message']}")
    
    print("\n✅ SDK示例完成")

if __name__ == "__main__":
    main()

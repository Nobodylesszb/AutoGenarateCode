#!/usr/bin/env python3
"""
测试新的支付架构
"""

import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000/api/v1"

def test_payment_architecture():
    """测试新的支付架构"""
    print("🚀 开始测试新的支付架构...")
    
    # 1. 测试获取支持的支付方式
    print("\n1. 测试获取支持的支付方式")
    try:
        response = requests.get(f"{BASE_URL}/payment/methods")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 支持的支付方式: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 获取支付方式失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
    
    # 2. 测试创建模拟支付
    print("\n2. 测试创建模拟支付")
    try:
        payment_data = {
            "product_id": "test_product",
            "product_name": "测试产品",
            "amount": 9.99,
            "currency": "CNY",
            "method": "mock",
            "buyer_id": "test_buyer_001",
            "buyer_name": "测试用户",
            "description": "测试支付订单"
        }
        
        response = requests.post(f"{BASE_URL}/payment/create", json=payment_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 支付创建成功: {json.dumps(data, ensure_ascii=False, indent=2)}")
            payment_id = data["payment_id"]
            
            # 3. 测试获取支付状态
            print("\n3. 测试获取支付状态")
            status_response = requests.get(f"{BASE_URL}/payment/status/{payment_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"✅ 支付状态: {json.dumps(status_data, ensure_ascii=False, indent=2)}")
            else:
                print(f"❌ 获取支付状态失败: {status_response.status_code}")
            
            # 4. 测试激活码
            if "activation_code" in data:
                activation_code = data["activation_code"]
                print(f"\n4. 测试激活码: {activation_code}")
                
                # 验证激活码
                verify_data = {
                    "code": activation_code,
                    "product_id": "test_product"
                }
                verify_response = requests.post(f"{BASE_URL}/activation/verify", json=verify_data)
                if verify_response.status_code == 200:
                    verify_result = verify_response.json()
                    print(f"✅ 激活码验证成功: {json.dumps(verify_result, ensure_ascii=False, indent=2)}")
                else:
                    print(f"❌ 激活码验证失败: {verify_response.status_code}")
            
        else:
            print(f"❌ 支付创建失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
    
    # 5. 测试微信支付（模拟）
    print("\n5. 测试微信支付（模拟）")
    try:
        wechat_payment_data = {
            "product_id": "test_product",
            "product_name": "测试产品",
            "amount": 19.99,
            "currency": "CNY",
            "method": "wechat",
            "buyer_id": "test_buyer_002",
            "buyer_name": "测试用户2",
            "description": "测试微信支付订单"
        }
        
        response = requests.post(f"{BASE_URL}/payment/create", json=wechat_payment_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 微信支付创建成功: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 微信支付创建失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
    
    # 6. 测试支付宝（模拟）
    print("\n6. 测试支付宝（模拟）")
    try:
        alipay_payment_data = {
            "product_id": "test_product",
            "product_name": "测试产品",
            "amount": 29.99,
            "currency": "CNY",
            "method": "alipay",
            "buyer_id": "test_buyer_003",
            "buyer_name": "测试用户3",
            "description": "测试支付宝订单"
        }
        
        response = requests.post(f"{BASE_URL}/payment/create", json=alipay_payment_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 支付宝创建成功: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 支付宝创建失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
    
    # 7. 测试支付统计
    print("\n7. 测试支付统计")
    try:
        response = requests.get(f"{BASE_URL}/payment/statistics")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 支付统计: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 获取支付统计失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
    
    # 8. 测试支付列表
    print("\n8. 测试支付列表")
    try:
        response = requests.get(f"{BASE_URL}/payment/list")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 支付列表: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 获取支付列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
    
    print("\n🎉 新支付架构测试完成！")

if __name__ == "__main__":
    test_payment_architecture()
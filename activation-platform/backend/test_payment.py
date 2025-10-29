#!/usr/bin/env python3
"""
支付功能测试脚本
测试支付相关的所有功能
"""

import requests
import json
import time
from decimal import Decimal

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_payment_functionality():
    """测试支付功能"""
    print("🧪 开始测试支付功能...")
    
    # 1. 测试创建支付并生成激活码
    print("\n1️⃣ 测试创建支付并生成激活码")
    try:
        response = requests.post(f"{BASE_URL}/payment/create-with-product", json={
            "product_id": "test_product_001",
            "product_name": "测试产品",
            "price": 99.00,
            "method": "wechat",
            "max_activations": 1,
            "return_url": "http://localhost:3000/payment/success"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 创建支付成功: {data['payment_id']}")
            print(f"   激活码: {data['activation_code']}")
            print(f"   支付链接: {data.get('payment_url', 'N/A')}")
            
            payment_id = data['payment_id']
            activation_code = data['activation_code']
        else:
            print(f"❌ 创建支付失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 创建支付异常: {e}")
        return False
    
    # 2. 测试获取支付状态
    print("\n2️⃣ 测试获取支付状态")
    try:
        response = requests.get(f"{BASE_URL}/payment/status/{payment_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取支付状态成功")
            print(f"   状态: {data['status']}")
            print(f"   金额: ¥{data['amount']}")
            print(f"   支付方式: {data['method']}")
        else:
            print(f"❌ 获取支付状态失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 获取支付状态异常: {e}")
    
    # 3. 测试获取支付统计
    print("\n3️⃣ 测试获取支付统计")
    try:
        response = requests.get(f"{BASE_URL}/payment/statistics")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取支付统计成功")
            print(f"   总金额: ¥{data['total_amount']}")
            print(f"   总订单: {data['total_orders']}")
            print(f"   今日金额: ¥{data['today_amount']}")
            print(f"   今日订单: {data['today_orders']}")
        else:
            print(f"❌ 获取支付统计失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 获取支付统计异常: {e}")
    
    # 4. 测试获取支付列表
    print("\n4️⃣ 测试获取支付列表")
    try:
        response = requests.get(f"{BASE_URL}/payment/list?skip=0&limit=10")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取支付列表成功")
            print(f"   列表长度: {len(data)}")
            if data:
                print(f"   第一个订单: {data[0]['payment_id']}")
        else:
            print(f"❌ 获取支付列表失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 获取支付列表异常: {e}")
    
    # 5. 测试激活码验证
    print("\n5️⃣ 测试激活码验证")
    try:
        response = requests.get(f"{BASE_URL}/activation/verify/{activation_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 激活码验证成功")
            print(f"   有效: {data['valid']}")
            print(f"   消息: {data['message']}")
            if data.get('activation_code'):
                print(f"   产品: {data['activation_code']['product_name']}")
                print(f"   剩余激活次数: {data.get('remaining_activations', 'N/A')}")
        else:
            print(f"❌ 激活码验证失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 激活码验证异常: {e}")
    
    # 6. 测试退款功能
    print("\n6️⃣ 测试退款功能")
    try:
        response = requests.post(f"{BASE_URL}/payment/refund", json={
            "payment_id": payment_id,
            "reason": "测试退款"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 退款处理成功")
            print(f"   消息: {data['message']}")
            print(f"   退款金额: ¥{data.get('refund_amount', 'N/A')}")
        else:
            print(f"❌ 退款处理失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 退款处理异常: {e}")
    
    # 7. 测试退款后的激活码状态
    print("\n7️⃣ 测试退款后的激活码状态")
    try:
        response = requests.get(f"{BASE_URL}/activation/verify/{activation_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 退款后激活码验证")
            print(f"   有效: {data['valid']}")
            print(f"   消息: {data['message']}")
        else:
            print(f"❌ 退款后激活码验证失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 退款后激活码验证异常: {e}")
    
    print("\n🎉 支付功能测试完成！")
    return True

def test_payment_callback():
    """测试支付回调功能"""
    print("\n🔄 测试支付回调功能...")
    
    # 模拟微信支付回调
    print("\n1️⃣ 测试微信支付回调")
    try:
        callback_data = {
            "out_trade_no": "PAY_TEST_001",
            "transaction_id": "WX_TRANSACTION_001",
            "result_code": "SUCCESS",
            "total_fee": "9900",  # 99.00元，单位为分
            "return_code": "SUCCESS"
        }
        
        response = requests.post(f"{BASE_URL}/payment/callback/wechat", data=callback_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 微信支付回调处理成功")
            print(f"   返回码: {data.get('return_code', 'N/A')}")
            print(f"   返回消息: {data.get('return_msg', 'N/A')}")
        else:
            print(f"❌ 微信支付回调处理失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 微信支付回调异常: {e}")
    
    # 模拟支付宝回调
    print("\n2️⃣ 测试支付宝回调")
    try:
        callback_data = {
            "out_trade_no": "PAY_TEST_002",
            "trade_no": "ALIPAY_TRADE_001",
            "trade_status": "TRADE_SUCCESS",
            "total_amount": "99.00"
        }
        
        response = requests.post(f"{BASE_URL}/payment/callback/alipay", data=callback_data)
        
        if response.status_code == 200:
            print(f"✅ 支付宝回调处理成功")
            print(f"   返回: {response.text}")
        else:
            print(f"❌ 支付宝回调处理失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 支付宝回调异常: {e}")

def main():
    """主函数"""
    print("🚀 支付功能测试开始")
    print("=" * 50)
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code != 200:
            print("❌ 服务器未运行，请先启动后端服务")
            return
    except:
        print("❌ 无法连接到服务器，请先启动后端服务")
        return
    
    # 运行测试
    success = test_payment_functionality()
    test_payment_callback()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 所有测试完成！")
    else:
        print("❌ 部分测试失败，请检查服务器状态")

if __name__ == "__main__":
    main()

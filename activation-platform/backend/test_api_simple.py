#!/usr/bin/env python3
"""
简化的多激活次数API测试
"""

import requests
import json

def test_api():
    """测试API端点"""
    base_url = "http://localhost:8000"
    
    print("🌐 测试多激活次数API")
    print("=" * 40)
    
    # 测试生成多激活次数的激活码
    print("1. 生成多激活次数的激活码:")
    try:
        response = requests.post(f"{base_url}/api/v1/activation/generate", json={
            "product_id": "api_test_multi",
            "product_name": "API测试多激活",
            "price": 299.00,
            "quantity": 1,
            "max_activations": 5
        })
        
        if response.status_code == 200:
            data = response.json()
            test_code = data[0]['code']
            print(f"   ✅ 生成成功: {test_code}")
            print(f"   最大激活次数: {data[0]['max_activations']}")
        else:
            print(f"   ❌ 生成失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ API调用异常: {e}")
        return False
    
    # 测试使用激活码
    print("\n2. 使用激活码:")
    try:
        response = requests.post(f"{base_url}/api/v1/activation/use", json={
            "code": test_code,
            "user_id": "api_test_user",
            "device_info": {"platform": "test"},
            "ip_address": "127.0.0.1"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 使用成功: {data['success']}")
            print(f"   消息: {data['message']}")
            print(f"   剩余激活次数: {data.get('remaining_activations', 0)}")
        else:
            print(f"   ❌ 使用失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"   ❌ API调用异常: {e}")
    
    # 测试获取激活记录
    print("\n3. 获取激活记录:")
    try:
        response = requests.get(f"{base_url}/api/v1/activation/records/{test_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 获取成功: {data['success']}")
            print(f"   当前激活次数: {data['current_activations']}")
            print(f"   剩余激活次数: {data['remaining_activations']}")
            print(f"   激活记录数量: {len(data['records'])}")
        else:
            print(f"   ❌ 获取失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"   ❌ API调用异常: {e}")
    
    # 测试验证激活码
    print("\n4. 验证激活码:")
    try:
        response = requests.get(f"{base_url}/api/v1/activation/verify/{test_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 验证成功: {data['valid']}")
            print(f"   消息: {data['message']}")
            if 'remaining_activations' in data:
                print(f"   剩余激活次数: {data['remaining_activations']}")
        else:
            print(f"   ❌ 验证失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"   ❌ API调用异常: {e}")
    
    return True

if __name__ == "__main__":
    test_api()

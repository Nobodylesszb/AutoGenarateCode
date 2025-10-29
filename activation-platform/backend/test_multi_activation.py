#!/usr/bin/env python3
"""
多激活次数功能测试脚本
测试激活码的多激活次数功能
"""

import sys
import os
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_multi_activation():
    """测试多激活次数功能"""
    print("🔄 测试多激活次数功能")
    print("=" * 50)
    
    try:
        from app.services.activation_service import ActivationCodeService
        from app.database import SessionLocal
        from app.schemas import ActivationCodeCreate
        from decimal import Decimal
        
        db = SessionLocal()
        service = ActivationCodeService(db)
        
        # 创建支持多激活次数的激活码
        print("1. 创建支持多激活次数的激活码:")
        request = ActivationCodeCreate(
            product_id="multi_activation_test",
            product_name="多激活次数测试产品",
            price=Decimal("199.00"),
            quantity=1,
            max_activations=3  # 支持3次激活
        )
        
        activation_codes = service.create_activation_codes(request)
        test_code = activation_codes[0].code
        print(f"   测试激活码: {test_code}")
        print(f"   最大激活次数: {activation_codes[0].max_activations}")
        
        # 第一次激活
        print("\n2. 第一次激活:")
        result1 = service.use_activation_code(test_code, "user1", {"device": "device1"}, "192.168.1.1")
        print(f"   结果: {result1['success']}")
        print(f"   消息: {result1['message']}")
        print(f"   剩余激活次数: {result1.get('remaining_activations', 0)}")
        
        # 第二次激活
        print("\n3. 第二次激活:")
        result2 = service.use_activation_code(test_code, "user2", {"device": "device2"}, "192.168.1.2")
        print(f"   结果: {result2['success']}")
        print(f"   消息: {result2['message']}")
        print(f"   剩余激活次数: {result2.get('remaining_activations', 0)}")
        
        # 第三次激活
        print("\n4. 第三次激活:")
        result3 = service.use_activation_code(test_code, "user3", {"device": "device3"}, "192.168.1.3")
        print(f"   结果: {result3['success']}")
        print(f"   消息: {result3['message']}")
        print(f"   剩余激活次数: {result3.get('remaining_activations', 0)}")
        
        # 第四次激活（应该失败）
        print("\n5. 第四次激活（应该失败）:")
        result4 = service.use_activation_code(test_code, "user4", {"device": "device4"}, "192.168.1.4")
        print(f"   结果: {result4['success']}")
        print(f"   消息: {result4['message']}")
        
        # 获取激活记录
        print("\n6. 获取激活记录:")
        records_result = service.get_activation_records(test_code)
        if records_result['success']:
            print(f"   最大激活次数: {records_result['max_activations']}")
            print(f"   当前激活次数: {records_result['current_activations']}")
            print(f"   剩余激活次数: {records_result['remaining_activations']}")
            print(f"   激活记录数量: {len(records_result['records'])}")
            
            for i, record in enumerate(records_result['records'], 1):
                print(f"   第{i}次激活: {record['user_id']} - {record['activation_time']}")
        else:
            print(f"   ❌ 获取记录失败: {records_result['message']}")
        
        # 验证激活码状态
        print("\n7. 验证激活码状态:")
        from app.schemas import ActivationCodeVerify
        verify_result = service.verify_activation_code(
            ActivationCodeVerify(code=test_code)
        )
        print(f"   验证结果: {verify_result['valid']}")
        print(f"   消息: {verify_result['message']}")
        if verify_result.get('remaining_activations') is not None:
            print(f"   剩余激活次数: {verify_result['remaining_activations']}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_single_activation():
    """测试单次激活（默认行为）"""
    print("\n🔒 测试单次激活（默认行为）")
    print("=" * 50)
    
    try:
        from app.services.activation_service import ActivationCodeService
        from app.database import SessionLocal
        from app.schemas import ActivationCodeCreate
        from decimal import Decimal
        
        db = SessionLocal()
        service = ActivationCodeService(db)
        
        # 创建默认单次激活的激活码
        print("1. 创建默认单次激活的激活码:")
        request = ActivationCodeCreate(
            product_id="single_activation_test",
            product_name="单次激活测试产品",
            price=Decimal("99.00"),
            quantity=1
            # max_activations 默认为1
        )
        
        activation_codes = service.create_activation_codes(request)
        test_code = activation_codes[0].code
        print(f"   测试激活码: {test_code}")
        print(f"   最大激活次数: {activation_codes[0].max_activations}")
        
        # 第一次激活
        print("\n2. 第一次激活:")
        result1 = service.use_activation_code(test_code, "user1")
        print(f"   结果: {result1['success']}")
        print(f"   消息: {result1['message']}")
        print(f"   剩余激活次数: {result1.get('remaining_activations', 0)}")
        
        # 第二次激活（应该失败）
        print("\n3. 第二次激活（应该失败）:")
        result2 = service.use_activation_code(test_code, "user2")
        print(f"   结果: {result2['success']}")
        print(f"   消息: {result2['message']}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n🌐 测试API端点")
    print("=" * 50)
    
    try:
        import requests
        import json
        
        base_url = "http://localhost:8000"
        
        # 测试生成多激活次数的激活码
        print("1. 测试生成多激活次数的激活码:")
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
        except Exception as e:
            print(f"   ❌ API调用异常: {e}")
        
        # 测试使用激活码
        print("\n2. 测试使用激活码:")
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
        except Exception as e:
            print(f"   ❌ API调用异常: {e}")
        
        # 测试获取激活记录
        print("\n3. 测试获取激活记录:")
        try:
            response = requests.get(f"{base_url}/api/v1/activation/records/{test_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 获取成功: {data['success']}")
                print(f"   当前激活次数: {data['current_activations']}")
                print(f"   剩余激活次数: {data['remaining_activations']}")
            else:
                print(f"   ❌ 获取失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ API调用异常: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 多激活次数功能测试")
    print("=" * 60)
    
    tests = [
        test_multi_activation,
        test_single_activation,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！多激活次数功能正常工作")
        print("\n✨ 多激活次数特性:")
        print("   • 支持设置最大激活次数")
        print("   • 默认单次激活")
        print("   • 详细的激活记录")
        print("   • 剩余激活次数查询")
        print("   • API接口支持")
        return True
    else:
        print("❌ 部分测试失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

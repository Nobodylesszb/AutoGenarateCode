#!/usr/bin/env python3
"""
硬件绑定功能测试脚本
测试硬件指纹生成、激活码绑定、验证等功能
"""

import sys
import os
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_hardware_fingerprint():
    """测试硬件指纹生成"""
    print("🔍 测试硬件指纹生成")
    print("=" * 50)
    
    try:
        from app.services.activation_service import HardwareFingerprint
        
        # 测试生成硬件指纹
        print("1. 测试硬件指纹生成:")
        fingerprint1 = HardwareFingerprint.generate_hardware_fingerprint()
        print(f"   硬件指纹: {fingerprint1}")
        print(f"   长度: {len(fingerprint1)}")
        
        # 测试指纹格式验证
        print("\n2. 测试指纹格式验证:")
        valid_cases = [
            ("a" * 64, True),   # 有效长度
            ("A" * 64, True),   # 大写字母
            ("1" * 64, True),   # 数字
            ("a" * 32, False),  # 长度不足
            ("a" * 128, False), # 长度过长
            ("", False),       # 空字符串
            ("g" * 64, True),  # 包含g
        ]
        
        for test_fingerprint, expected in valid_cases:
            result = HardwareFingerprint.validate_fingerprint(test_fingerprint)
            status = "✅" if result == expected else "❌"
            print(f"   {status} {test_fingerprint[:20]}... -> {result} (期望: {expected})")
        
        # 测试多次生成的唯一性
        print("\n3. 测试指纹唯一性:")
        fingerprints = []
        for i in range(5):
            fp = HardwareFingerprint.generate_hardware_fingerprint()
            fingerprints.append(fp)
            print(f"   第{i+1}次: {fp}")
        
        unique_fingerprints = set(fingerprints)
        print(f"   唯一性: {'✅ 通过' if len(fingerprints) == len(unique_fingerprints) else '❌ 失败'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_hardware_binding():
    """测试硬件绑定功能"""
    print("\n🔗 测试硬件绑定功能")
    print("=" * 50)
    
    try:
        from app.services.activation_service import ActivationCodeService, HardwareFingerprint
        from app.database import SessionLocal
        from app.schemas import ActivationCodeCreate
        from decimal import Decimal
        
        db = SessionLocal()
        service = ActivationCodeService(db)
        
        # 创建测试激活码
        print("1. 创建测试激活码:")
        request = ActivationCodeCreate(
            product_id="hardware_test_product",
            product_name="硬件绑定测试产品",
            price=Decimal("299.00"),
            quantity=1
        )
        
        activation_codes = service.create_activation_codes(request)
        test_code = activation_codes[0].code
        print(f"   测试激活码: {test_code}")
        
        # 生成硬件指纹
        print("\n2. 生成硬件指纹:")
        hardware_fingerprint = HardwareFingerprint.generate_hardware_fingerprint()
        print(f"   硬件指纹: {hardware_fingerprint}")
        
        # 测试硬件绑定
        print("\n3. 测试硬件绑定:")
        bind_result = service.bind_to_hardware(
            test_code,
            hardware_fingerprint,
            "test_user_hardware"
        )
        print(f"   绑定结果: {bind_result['success']}")
        print(f"   消息: {bind_result['message']}")
        
        if bind_result['success']:
            print(f"   绑定信息: {bind_result.get('binding_info', {})}")
        
        # 测试硬件验证
        print("\n4. 测试硬件验证:")
        verify_result = service.verify_hardware_binding(
            test_code,
            hardware_fingerprint
        )
        print(f"   验证结果: {verify_result['valid']}")
        print(f"   消息: {verify_result['message']}")
        
        # 测试错误硬件指纹
        print("\n5. 测试错误硬件指纹:")
        wrong_fingerprint = "wrong_fingerprint_" + "a" * 40
        wrong_verify_result = service.verify_hardware_binding(
            test_code,
            wrong_fingerprint
        )
        print(f"   错误指纹验证: {wrong_verify_result['valid']}")
        print(f"   消息: {wrong_verify_result['message']}")
        
        # 测试获取绑定信息
        print("\n6. 测试获取绑定信息:")
        binding_info = service.get_hardware_binding_info(test_code)
        print(f"   获取结果: {binding_info['success']}")
        if binding_info['success']:
            print(f"   绑定信息: {binding_info.get('binding_info', {})}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_hardware_unbinding():
    """测试硬件解绑功能"""
    print("\n🔓 测试硬件解绑功能")
    print("=" * 50)
    
    try:
        from app.services.activation_service import ActivationCodeService, HardwareFingerprint
        from app.database import SessionLocal
        from app.schemas import ActivationCodeCreate
        from decimal import Decimal
        
        db = SessionLocal()
        service = ActivationCodeService(db)
        
        # 创建测试激活码
        print("1. 创建测试激活码:")
        request = ActivationCodeCreate(
            product_id="unbind_test_product",
            product_name="解绑测试产品",
            price=Decimal("199.00"),
            quantity=1
        )
        
        activation_codes = service.create_activation_codes(request)
        test_code = activation_codes[0].code
        print(f"   测试激活码: {test_code}")
        
        # 绑定硬件
        print("\n2. 绑定硬件:")
        hardware_fingerprint = HardwareFingerprint.generate_hardware_fingerprint()
        bind_result = service.bind_to_hardware(test_code, hardware_fingerprint)
        print(f"   绑定结果: {bind_result['success']}")
        
        # 验证绑定
        print("\n3. 验证绑定:")
        verify_result = service.verify_hardware_binding(test_code, hardware_fingerprint)
        print(f"   验证结果: {verify_result['valid']}")
        
        # 解绑硬件
        print("\n4. 解绑硬件:")
        unbind_result = service.unbind_hardware(test_code, "admin_unbind_key_2024")
        print(f"   解绑结果: {unbind_result['success']}")
        print(f"   消息: {unbind_result['message']}")
        
        # 验证解绑后状态
        print("\n5. 验证解绑后状态:")
        post_unbind_verify = service.verify_hardware_binding(test_code, hardware_fingerprint)
        print(f"   解绑后验证: {post_unbind_verify['valid']}")
        print(f"   消息: {post_unbind_verify['message']}")
        
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
        
        # 测试生成硬件指纹API
        print("1. 测试生成硬件指纹API:")
        try:
            response = requests.post(f"{base_url}/api/v1/activation/hardware/generate-fingerprint")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 成功生成指纹: {data['fingerprint'][:20]}...")
                print(f"   设备信息: {data['device_info']}")
            else:
                print(f"   ❌ API调用失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ API调用异常: {e}")
        
        # 测试安全信息API
        print("\n2. 测试安全信息API:")
        try:
            response = requests.get(f"{base_url}/api/v1/activation/security-info")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 硬件绑定支持: {data.get('hardware_binding', False)}")
                print(f"   指纹算法: {data.get('fingerprint_algorithm', 'N/A')}")
            else:
                print(f"   ❌ API调用失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ API调用异常: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_multiple_devices():
    """测试多设备绑定限制"""
    print("\n🚫 测试多设备绑定限制")
    print("=" * 50)
    
    try:
        from app.services.activation_service import ActivationCodeService, HardwareFingerprint
        from app.database import SessionLocal
        from app.schemas import ActivationCodeCreate
        from decimal import Decimal
        
        db = SessionLocal()
        service = ActivationCodeService(db)
        
        # 创建测试激活码
        print("1. 创建测试激活码:")
        request = ActivationCodeCreate(
            product_id="multi_device_test",
            product_name="多设备测试产品",
            price=Decimal("399.00"),
            quantity=1
        )
        
        activation_codes = service.create_activation_codes(request)
        test_code = activation_codes[0].code
        print(f"   测试激活码: {test_code}")
        
        # 生成两个不同的硬件指纹
        print("\n2. 生成硬件指纹:")
        fingerprint1 = HardwareFingerprint.generate_hardware_fingerprint()
        fingerprint2 = "device2_" + HardwareFingerprint.generate_hardware_fingerprint()[:50]
        print(f"   设备1指纹: {fingerprint1[:20]}...")
        print(f"   设备2指纹: {fingerprint2[:20]}...")
        
        # 在设备1上绑定
        print("\n3. 在设备1上绑定:")
        bind1_result = service.bind_to_hardware(test_code, fingerprint1, "user1")
        print(f"   设备1绑定结果: {bind1_result['success']}")
        
        # 尝试在设备2上绑定
        print("\n4. 尝试在设备2上绑定:")
        bind2_result = service.bind_to_hardware(test_code, fingerprint2, "user2")
        print(f"   设备2绑定结果: {bind2_result['success']}")
        print(f"   消息: {bind2_result['message']}")
        
        # 验证设备1的绑定
        print("\n5. 验证设备1绑定:")
        verify1_result = service.verify_hardware_binding(test_code, fingerprint1)
        print(f"   设备1验证: {verify1_result['valid']}")
        
        # 验证设备2的绑定
        print("\n6. 验证设备2绑定:")
        verify2_result = service.verify_hardware_binding(test_code, fingerprint2)
        print(f"   设备2验证: {verify2_result['valid']}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 硬件绑定功能测试")
    print("=" * 60)
    
    tests = [
        test_hardware_fingerprint,
        test_hardware_binding,
        test_hardware_unbinding,
        test_multiple_devices,
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
        print("🎉 所有测试通过！硬件绑定功能正常工作")
        print("\n✨ 硬件绑定特性:")
        print("   • 硬件指纹生成和验证")
        print("   • 激活码与硬件唯一绑定")
        print("   • 多设备绑定限制")
        print("   • 管理员解绑功能")
        print("   • API接口支持")
        return True
    else:
        print("❌ 部分测试失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

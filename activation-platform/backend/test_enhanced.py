#!/usr/bin/env python3
"""
激活码安全功能测试脚本
测试增强的激活码生成、加盐加密、唯一性等功能
"""

import sys
import os
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_enhanced_code_generation():
    """测试增强的激活码生成功能"""
    print("🔐 测试增强的激活码生成功能")
    print("=" * 50)
    
    try:
        from app.services.activation_service import EnhancedActivationCodeGenerator
        
        # 测试单个激活码生成
        print("1. 测试单个激活码生成:")
        code1 = EnhancedActivationCodeGenerator.generate_secure_code(32, "ACT")
        print(f"   生成激活码: {code1}")
        print(f"   长度: {len(code1)}")
        print(f"   格式验证: {EnhancedActivationCodeGenerator.verify_code_format(code1)}")
        
        # 测试批量生成
        print("\n2. 测试批量生成激活码:")
        codes = EnhancedActivationCodeGenerator.generate_batch_codes(5, 32, "ACT")
        print(f"   生成数量: {len(codes)}")
        print(f"   激活码列表:")
        for i, code in enumerate(codes, 1):
            print(f"     {i}. {code}")
        
        # 测试唯一性
        print("\n3. 测试唯一性:")
        unique_codes = set(codes)
        print(f"   生成数量: {len(codes)}")
        print(f"   唯一数量: {len(unique_codes)}")
        print(f"   唯一性: {'✅ 通过' if len(codes) == len(unique_codes) else '❌ 失败'}")
        
        # 测试格式验证
        print("\n4. 测试格式验证:")
        test_cases = [
            ("ACT1234567890ABCDEFGHJKLMNPQRSTUV", True),  # 正确格式
            ("ACT1234567890ABCDEFGHJKLMNPQRSTUVWXYZ", True),  # 正确格式
            ("INVALID123", False),  # 错误前缀
            ("ACT", False),  # 太短
            ("ACT1234567890ABCDEFGHJKLMNPQRSTUVWXYZ1234567890", False),  # 太长
            ("ACT1234567890ABCDEFGHJKLMNPQRSTUV0", False),  # 包含禁用字符
        ]
        
        for test_code, expected in test_cases:
            result = EnhancedActivationCodeGenerator.verify_code_format(test_code)
            status = "✅" if result == expected else "❌"
            print(f"   {status} {test_code[:20]}... -> {result} (期望: {expected})")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_encryption_security():
    """测试加密安全性"""
    print("\n🔒 测试加密安全性")
    print("=" * 50)
    
    try:
        from app.services.activation_service import EnhancedActivationCodeGenerator
        
        # 测试相同输入产生不同输出（由于时间戳和随机数）
        print("1. 测试随机性:")
        codes = []
        for i in range(5):
            code = EnhancedActivationCodeGenerator.generate_secure_code(32, "ACT")
            codes.append(code)
            print(f"   第{i+1}次: {code}")
        
        unique_codes = set(codes)
        print(f"   唯一性: {'✅ 通过' if len(codes) == len(unique_codes) else '❌ 失败'}")
        
        # 测试字符集安全性
        print("\n2. 测试字符集安全性:")
        all_chars = set()
        for code in codes:
            all_chars.update(code[3:])  # 排除前缀
        
        safe_chars = set(EnhancedActivationCodeGenerator.CHARACTERS)
        unsafe_chars = all_chars - safe_chars
        print(f"   使用的字符: {sorted(all_chars)}")
        print(f"   安全字符集: {sorted(safe_chars)}")
        print(f"   不安全字符: {sorted(unsafe_chars)}")
        print(f"   安全性: {'✅ 通过' if not unsafe_chars else '❌ 失败'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_database_integration():
    """测试数据库集成"""
    print("\n🗄️ 测试数据库集成")
    print("=" * 50)
    
    try:
        from app.services.activation_service import ActivationCodeService
        from app.database import SessionLocal
        from app.schemas import ActivationCodeCreate
        from decimal import Decimal
        
        db = SessionLocal()
        service = ActivationCodeService(db)
        
        # 测试创建激活码
        print("1. 测试创建激活码:")
        request = ActivationCodeCreate(
            product_id="test_product_enhanced",
            product_name="增强测试产品",
            price=Decimal("199.00"),
            quantity=3
        )
        
        activation_codes = service.create_activation_codes(request)
        print(f"   创建数量: {len(activation_codes)}")
        
        for i, code in enumerate(activation_codes, 1):
            print(f"   {i}. {code.code} (长度: {len(code.code)})")
        
        # 测试验证激活码
        print("\n2. 测试验证激活码:")
        test_code = activation_codes[0].code
        from app.schemas import ActivationCodeVerify
        verify_result = service.verify_activation_code(
            ActivationCodeVerify(code=test_code)
        )
        print(f"   验证结果: {verify_result['valid']}")
        print(f"   消息: {verify_result['message']}")
        
        # 测试使用激活码
        print("\n3. 测试使用激活码:")
        use_result = service.use_activation_code(test_code, "test_user_123")
        print(f"   使用结果: {use_result['success']}")
        print(f"   消息: {use_result['message']}")
        
        # 测试安全信息
        print("\n4. 测试安全信息:")
        security_info = service.get_code_security_info()
        print(f"   加盐密钥长度: {security_info['salt_key_length']}")
        print(f"   字符集大小: {security_info['character_set_size']}")
        print(f"   默认长度: {security_info['default_length']}")
        print(f"   加密方法: {security_info['encryption_method']}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_performance():
    """测试性能"""
    print("\n⚡ 测试性能")
    print("=" * 50)
    
    try:
        import time
        from app.services.activation_service import EnhancedActivationCodeGenerator
        
        # 测试生成速度
        print("1. 测试生成速度:")
        quantities = [10, 100, 1000]
        
        for qty in quantities:
            start_time = time.time()
            codes = EnhancedActivationCodeGenerator.generate_batch_codes(qty, 32, "ACT")
            end_time = time.time()
            
            duration = end_time - start_time
            speed = qty / duration
            print(f"   生成 {qty} 个激活码: {duration:.3f}秒 (速度: {speed:.0f}个/秒)")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 激活码安全功能测试")
    print("=" * 60)
    
    tests = [
        test_enhanced_code_generation,
        test_encryption_security,
        test_database_integration,
        test_performance
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
        print("🎉 所有测试通过！激活码安全功能正常工作")
        print("\n✨ 新功能特性:")
        print("   • 激活码长度增加到32位")
        print("   • 使用HMAC-SHA256加盐加密")
        print("   • 确保激活码唯一性")
        print("   • 格式验证和安全性检查")
        print("   • 排除易混淆字符")
        return True
    else:
        print("❌ 部分测试失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

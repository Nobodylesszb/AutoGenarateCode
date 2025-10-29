#!/usr/bin/env python3
"""
激活码平台测试脚本
用于验证项目是否可以正常运行
"""

import sys
import os
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from app.config import settings
        print("✅ 配置模块导入成功")
        
        from app.database import Base, engine
        print("✅ 数据库模块导入成功")
        
        from app.models import ActivationCode, Payment, User, Product
        print("✅ 数据模型导入成功")
        
        from app.schemas import ActivationCodeCreate, PaymentCreate
        print("✅ 数据模式导入成功")
        
        from app.services.activation_service import ActivationCodeService
        print("✅ 激活码服务导入成功")
        
        from app.services.payment_service import PaymentService
        print("✅ 支付服务导入成功")
        
        from app.api.activation import router as activation_router
        print("✅ 激活码API导入成功")
        
        from app.api.payment import router as payment_router
        print("✅ 支付API导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_database_creation():
    """测试数据库创建"""
    print("\n🗄️ 测试数据库创建...")
    
    try:
        from app.database import Base, engine
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库创建失败: {e}")
        return False

def test_fastapi_app():
    """测试FastAPI应用创建"""
    print("\n🚀 测试FastAPI应用创建...")
    
    try:
        from app.main import app
        print("✅ FastAPI应用创建成功")
        
        # 检查路由
        routes = [route.path for route in app.routes]
        print(f"✅ 发现 {len(routes)} 个路由")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI应用创建失败: {e}")
        return False

def test_activation_service():
    """测试激活码服务"""
    print("\n🔑 测试激活码服务...")
    
    try:
        from app.services.activation_service import ActivationCodeGenerator
        
        # 测试激活码生成
        code = ActivationCodeGenerator.generate_code()
        print(f"✅ 生成激活码: {code}")
        
        # 测试批量生成
        codes = ActivationCodeGenerator.generate_batch_codes(3)
        print(f"✅ 批量生成激活码: {len(codes)} 个")
        
        return True
        
    except Exception as e:
        print(f"❌ 激活码服务测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 激活码平台测试")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database_creation,
        test_fastapi_app,
        test_activation_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！项目可以正常运行")
        print("\n🚀 启动命令:")
        print("   python start.py")
        print("   或")
        print("   uvicorn app.main:app --reload")
        return True
    else:
        print("❌ 部分测试失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

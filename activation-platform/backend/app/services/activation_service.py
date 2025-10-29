import secrets
import string
import hashlib
import wmi
import hmac
import time
import uuid
import json
import platform
import psutil
from typing import List, Optional, Set, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import ActivationCode, ActivationCodeStatus, Product
from app.schemas import ActivationCodeCreate, ActivationCodeVerify
from app.config import settings
import json

class HardwareFingerprint:
    """硬件指纹生成器"""
    
    @staticmethod
    def generate_hardware_fingerprint() -> str:
        """
        生成硬件指纹
        基于多个硬件特征生成唯一标识
        """
        try:
            # 收集硬件信息
            hardware_info = {
                # CPU信息
                'cpu_count': psutil.cpu_count(),
                'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                
                # 内存信息
                'memory_total': psutil.virtual_memory().total,
                
                # 磁盘信息
                'disk_info': HardwareFingerprint._get_disk_serial(),
                
                # 网络信息
                'mac_address': HardwareFingerprint._get_mac_address(),
                
                # 系统信息
                'platform': platform.platform(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                
                # 主板信息（如果可用）
                'motherboard': HardwareFingerprint._get_motherboard_info(),
            }
            
            # 生成指纹
            fingerprint_data = json.dumps(hardware_info, sort_keys=True)
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
            return fingerprint
            
        except Exception as e:
            # 如果无法获取硬件信息，使用备用方案
            return HardwareFingerprint._generate_fallback_fingerprint()
    
    @staticmethod
    def _get_disk_serial() -> str:
        """获取磁盘序列号"""
        try:
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                if disk.SerialNumber:
                    return disk.SerialNumber
        except:
            pass
        
        try:
            # Linux/Mac 备用方案
            import subprocess
            result = subprocess.run(['lsblk', '-o', 'SERIAL'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
        except:
            pass
        
        return "unknown_disk"
    
    @staticmethod
    def _get_mac_address() -> str:
        """获取MAC地址"""
        try:
            import uuid
            mac = uuid.getnode()
            return ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
        except:
            return "unknown_mac"
    
    @staticmethod
    def _get_motherboard_info() -> str:
        """获取主板信息"""
        try:
            import wmi
            c = wmi.WMI()
            for board in c.Win32_BaseBoard():
                if board.SerialNumber:
                    return board.SerialNumber
        except:
            pass
        
        return "unknown_motherboard"
    
    @staticmethod
    def _generate_fallback_fingerprint() -> str:
        """生成备用指纹"""
        try:
            # 使用可用的系统信息
            fallback_info = {
                'hostname': platform.node(),
                'platform': platform.platform(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'timestamp': str(int(time.time()))
            }
            
            fingerprint_data = json.dumps(fallback_info, sort_keys=True)
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
            return fingerprint
            
        except Exception:
            # 最后的备用方案
            return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    
    @staticmethod
    def validate_fingerprint(fingerprint: str) -> bool:
        """验证指纹格式"""
        if not fingerprint or len(fingerprint) != 64:
            return False
        
        # 检查是否为有效的十六进制字符串
        try:
            int(fingerprint, 16)
            return True
        except ValueError:
            return False

class HardwareBindingService:
    """硬件绑定服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def bind_activation_code_to_hardware(self, activation_code_id: int, hardware_fingerprint: str, user_id: str = None) -> Dict[str, Any]:
        """
        将激活码绑定到硬件
        
        Args:
            activation_code_id: 激活码ID
            hardware_fingerprint: 硬件指纹
            user_id: 用户ID
            
        Returns:
            绑定结果
        """
        try:
            # 验证硬件指纹格式
            if not HardwareFingerprint.validate_fingerprint(hardware_fingerprint):
                return {
                    
                    "success": False,
                    "message": "无效的硬件指纹格式"
                }
            
            # 获取激活码
            activation_code = self.db.query(ActivationCode).filter(
                ActivationCode.id == activation_code_id
            ).first()
            
            if not activation_code:
                return {
                    "success": False,
                    "message": "激活码不存在"
                }
            
            # 检查激活码状态
            if activation_code.status != ActivationCodeStatus.UNUSED:
                return {
                    "success": False,
                    "message": "激活码已被使用或不可用"
                }
            
            # 检查是否已绑定其他硬件
            existing_binding = self.db.query(ActivationCode).filter(
                ActivationCode.id == activation_code_id,
                ActivationCode.metadata_json.isnot(None)
            ).first()
            
            if existing_binding and existing_binding.metadata_json:
                try:
                    metadata = json.loads(existing_binding.metadata_json)
                    if metadata.get('hardware_fingerprint'):
                        return {
                            "success": False,
                            "message": "激活码已绑定到其他硬件设备"
                        }
                except:
                    pass
            
            # 检查该硬件是否已绑定其他激活码
            hardware_bindings = self.db.query(ActivationCode).filter(
                ActivationCode.metadata_json.like(f'%{hardware_fingerprint}%'),
                ActivationCode.status == ActivationCodeStatus.USED
            ).all()
            
            if hardware_bindings:
                return {
                    "success": False,
                    "message": "该硬件设备已绑定其他激活码"
                }
            
            # 执行绑定
            binding_metadata = {
                "hardware_fingerprint": hardware_fingerprint,
                "binding_time": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "binding_ip": "unknown",  # 可以从请求中获取
                "device_info": {
                    "platform": platform.platform(),
                    "machine": platform.machine(),
                    "processor": platform.processor()
                }
            }
            
            activation_code.metadata_json = json.dumps(binding_metadata)
            activation_code.status = ActivationCodeStatus.USED
            activation_code.used_at = datetime.utcnow()
            activation_code.used_by = user_id
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "硬件绑定成功",
                "activation_code": activation_code,
                "binding_info": binding_metadata
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"硬件绑定失败: {str(e)}"
            }
    
    def verify_hardware_binding(self, activation_code: str, hardware_fingerprint: str) -> Dict[str, Any]:
        """
        验证硬件绑定
        
        Args:
            activation_code: 激活码
            hardware_fingerprint: 硬件指纹
            
        Returns:
            验证结果
        """
        try:
            # 验证硬件指纹格式
            if not HardwareFingerprint.validate_fingerprint(hardware_fingerprint):
                return {
                    "valid": False,
                    "message": "无效的硬件指纹格式"
                }
            
            # 获取激活码
            code_record = self.db.query(ActivationCode).filter(
                ActivationCode.code == activation_code
            ).first()
            
            if not code_record:
                return {
                    "valid": False,
                    "message": "激活码不存在"
                }
            
            # 检查激活码状态
            if code_record.status != ActivationCodeStatus.USED:
                return {
                    "valid": False,
                    "message": "激活码未激活"
                }
            
            # 检查硬件绑定
            if not code_record.metadata_json:
                return {
                    "valid": False,
                    "message": "激活码未绑定硬件"
                }
            
            try:
                metadata = json.loads(code_record.metadata_json)
                bound_fingerprint = metadata.get('hardware_fingerprint')
                
                if not bound_fingerprint:
                    return {
                        "valid": False,
                        "message": "激活码未绑定硬件"
                    }
                
                if bound_fingerprint != hardware_fingerprint:
                    return {
                        "valid": False,
                        "message": "硬件指纹不匹配，可能在其他设备上使用"
                    }
                
                return {
                    "valid": True,
                    "message": "硬件绑定验证通过",
                    "binding_info": metadata
                }
                
            except json.JSONDecodeError:
                return {
                    "valid": False,
                    "message": "激活码绑定信息损坏"
                }
                
        except Exception as e:
            return {
                "valid": False,
                "message": f"验证失败: {str(e)}"
            }
    
    def get_hardware_binding_info(self, activation_code: str) -> Dict[str, Any]:
        """
        获取硬件绑定信息
        
        Args:
            activation_code: 激活码
            
        Returns:
            绑定信息
        """
        try:
            code_record = self.db.query(ActivationCode).filter(
                ActivationCode.code == activation_code
            ).first()
            
            if not code_record:
                return {
                    "success": False,
                    "message": "激活码不存在"
                }
            
            if not code_record.metadata_json:
                return {
                    "success": False,
                    "message": "激活码未绑定硬件"
                }
            
            try:
                metadata = json.loads(code_record.metadata_json)
                return {
                    "success": True,
                    "binding_info": metadata,
                    "activation_code": {
                        "code": code_record.code,
                        "product_name": code_record.product_name,
                        "status": code_record.status.value,
                        "used_at": code_record.used_at.isoformat() if code_record.used_at else None,
                        "used_by": code_record.used_by
                    }
                }
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "message": "绑定信息格式错误"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"获取绑定信息失败: {str(e)}"
            }
    
    def unbind_hardware(self, activation_code: str, admin_key: str = None) -> Dict[str, Any]:
        """
        解绑硬件（管理员功能）
        
        Args:
            activation_code: 激活码
            admin_key: 管理员密钥
            
        Returns:
            解绑结果
        """
        try:
            # 这里可以添加管理员权限验证
            if admin_key != settings.ADMIN_UNBIND_KEY:
                return {
                    "success": False,
                    "message": "无权限执行此操作"
                }
            
            code_record = self.db.query(ActivationCode).filter(
                ActivationCode.code == activation_code
            ).first()
            
            if not code_record:
                return {
                    "success": False,
                    "message": "激活码不存在"
                }
            
            # 清除绑定信息
            code_record.metadata_json = None
            code_record.status = ActivationCodeStatus.UNUSED
            code_record.used_at = None
            code_record.used_by = None
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "硬件解绑成功"
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"解绑失败: {str(e)}"
            }

class EnhancedActivationCodeGenerator:
    """增强的激活码生成器 - 支持加盐加密、增加长度、确保唯一性"""
    
    # 加盐密钥 - 生产环境中应该从环境变量获取
    SALT_KEY = "activation_platform_salt_2024"
    
    # 字符集 - 排除容易混淆的字符
    CHARACTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # 排除 I, O, 0, 1
    
    @classmethod
    def generate_secure_code(cls, length: int = 32, prefix: str = "ACT") -> str:
        """
        生成安全的激活码
        
        Args:
            length: 激活码总长度（包含前缀）
            prefix: 前缀
            
        Returns:
            生成的激活码
        """
        # 计算随机部分长度
        random_length = length - len(prefix)
        
        # 生成随机字符串
        random_part = ''.join(secrets.choice(cls.CHARACTERS) for _ in range(random_length))
        
        # 添加时间戳和随机数增加唯一性
        timestamp = str(int(time.time()))[-6:]  # 取时间戳后6位
        random_suffix = secrets.token_hex(4).upper()[:4]  # 8位随机hex转大写取前4位
        
        # 组合原始字符串
        raw_string = f"{prefix}{random_part}{timestamp}{random_suffix}"
        
        # 使用HMAC加盐加密
        encrypted_code = cls._encrypt_with_salt(raw_string)
        
        # 截取到指定长度并格式化
        final_code = cls._format_code(encrypted_code, length, prefix)
        
        return final_code
    
    @classmethod
    def _encrypt_with_salt(cls, raw_string: str) -> str:
        """
        使用HMAC加盐加密字符串
        
        Args:
            raw_string: 原始字符串
            
        Returns:
            加密后的字符串
        """
        # 使用HMAC-SHA256进行加密
        encrypted = hmac.new(
            cls.SALT_KEY.encode('utf-8'),
            raw_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()
        
        return encrypted
    
    @classmethod
    def _format_code(cls, encrypted_string: str, target_length: int, prefix: str) -> str:
        """
        格式化激活码，确保长度和可读性
        
        Args:
            encrypted_string: 加密后的字符串
            target_length: 目标长度
            prefix: 前缀
            
        Returns:
            格式化后的激活码
        """
        # 从加密字符串中提取字符，确保只使用安全字符集
        safe_chars = []
        for char in encrypted_string:
            if char in cls.CHARACTERS:
                safe_chars.append(char)
        
        # 如果安全字符不够，用随机字符补充
        while len(safe_chars) < target_length - len(prefix):
            safe_chars.append(secrets.choice(cls.CHARACTERS))
        
        # 截取到目标长度
        random_part = ''.join(safe_chars[:target_length - len(prefix)])
        
        return f"{prefix}{random_part}"
    
    @classmethod
    def generate_batch_codes(cls, count: int, length: int = 32, prefix: str = "ACT") -> List[str]:
        """
        批量生成唯一的激活码
        
        Args:
            count: 生成数量
            length: 激活码长度
            prefix: 前缀
            
        Returns:
            激活码列表
        """
        codes: Set[str] = set()
        max_attempts = count * 10  # 最大尝试次数，防止无限循环
        attempts = 0
        
        while len(codes) < count and attempts < max_attempts:
            code = cls.generate_secure_code(length, prefix)
            codes.add(code)
            attempts += 1
        
        if len(codes) < count:
            raise Exception(f"无法生成足够的唯一激活码，尝试了 {max_attempts} 次")
        
        return list(codes)
    
    @classmethod
    def verify_code_format(cls, code: str, expected_prefix: str = "ACT") -> bool:
        """
        验证激活码格式
        
        Args:
            code: 激活码
            expected_prefix: 期望的前缀
            
        Returns:
            格式是否正确
        """
        if not code or len(code) < 8:
            return False
        
        if not code.startswith(expected_prefix):
            return False
        
        # 检查是否只包含安全字符
        for char in code[len(expected_prefix):]:
            if char not in cls.CHARACTERS:
                return False
        
        return True

class ActivationCodeGenerator:
    """激活码生成器 - 保持向后兼容"""
    
    @staticmethod
    def generate_code(length: int = None, prefix: str = None) -> str:
        """生成激活码 - 使用增强版本"""
        if length is None:
            length = settings.ACTIVATION_CODE_LENGTH
        if prefix is None:
            prefix = settings.ACTIVATION_CODE_PREFIX
        
        # 使用增强的生成器
        return EnhancedActivationCodeGenerator.generate_secure_code(length, prefix)
    
    @staticmethod
    def generate_batch_codes(count: int, length: int = None, prefix: str = None) -> List[str]:
        """批量生成激活码 - 使用增强版本"""
        if length is None:
            length = settings.ACTIVATION_CODE_LENGTH
        if prefix is None:
            prefix = settings.ACTIVATION_CODE_PREFIX
        
        # 使用增强的生成器
        return EnhancedActivationCodeGenerator.generate_batch_codes(count, length, prefix)

class ActivationCodeService:
    """激活码服务 - 支持硬件绑定"""
    
    def __init__(self, db: Session):
        self.db = db
        self.hardware_service = HardwareBindingService(db)
    
    def create_activation_codes(self, request: ActivationCodeCreate) -> List[ActivationCode]:
        """创建激活码 - 增强版本，确保唯一性"""
        # 使用增强的生成器
        codes = EnhancedActivationCodeGenerator.generate_batch_codes(
            request.quantity,
            length=32,  # 增加长度到32位
            prefix=settings.ACTIVATION_CODE_PREFIX
        )
        
        # 检查数据库中是否已存在这些激活码
        existing_codes = self._check_existing_codes(codes)
        if existing_codes:
            # 如果存在重复，重新生成
            codes = self._regenerate_unique_codes(request.quantity, existing_codes)
        
        activation_codes = []
        for code in codes:
            activation_code = ActivationCode(
                code=code,
                product_id=request.product_id,
                product_name=request.product_name,
                price=request.price,
                currency=request.currency,
                expires_at=request.expires_at,
                metadata_json=json.dumps(request.metadata_json) if request.metadata_json else None,
                max_activations=request.max_activations,
                current_activations=0
            )
            self.db.add(activation_code)
            activation_codes.append(activation_code)
        
        self.db.commit()
        return activation_codes
    
    def _check_existing_codes(self, codes: List[str]) -> Set[str]:
        """检查激活码是否已存在"""
        existing = self.db.query(ActivationCode.code).filter(
            ActivationCode.code.in_(codes)
        ).all()
        return {code[0] for code in existing}
    
    def _regenerate_unique_codes(self, count: int, existing_codes: Set[str]) -> List[str]:
        """重新生成唯一的激活码"""
        codes = set()
        max_attempts = count * 20
        attempts = 0
        
        while len(codes) < count and attempts < max_attempts:
            code = EnhancedActivationCodeGenerator.generate_secure_code(32, settings.ACTIVATION_CODE_PREFIX)
            if code not in existing_codes and code not in codes:
                codes.add(code)
            attempts += 1
        
        if len(codes) < count:
            raise Exception(f"无法生成足够的唯一激活码")
        
        return list(codes)
    
    def get_activation_code(self, code: str) -> Optional[ActivationCode]:
        """获取激活码"""
        return self.db.query(ActivationCode).filter(ActivationCode.code == code).first()
    
    def verify_activation_code(self, request: ActivationCodeVerify) -> dict:
        """验证激活码"""
        # 首先验证格式
        if not EnhancedActivationCodeGenerator.verify_code_format(request.code):
            return {
                "valid": False,
                "message": "激活码格式不正确"
            }
        
        activation_code = self.get_activation_code(request.code)
        
        if not activation_code:
            return {
                "valid": False,
                "message": "激活码不存在"
            }
        
        # 检查激活次数
        if activation_code.current_activations >= activation_code.max_activations:
            return {
                "valid": False,
                "message": f"激活码已达到最大激活次数({activation_code.max_activations}次)"
            }
        
        if activation_code.status == ActivationCodeStatus.DISABLED:
            return {
                "valid": False,
                "message": "激活码已被禁用"
            }
        
        # 检查过期时间
        if activation_code.expires_at and activation_code.expires_at < datetime.utcnow():
            return {
                "valid": False,
                "message": "激活码已过期"
            }
        
        return {
            "valid": True,
            "message": "激活码有效",
            "activation_code": activation_code,
            "remaining_activations": activation_code.max_activations - activation_code.current_activations
        }
    
    def use_activation_code(self, code: str, user_id: str = None, device_info: dict = None, ip_address: str = None) -> dict:
        """使用激活码（支持多激活次数）"""
        # 首先验证格式
        if not EnhancedActivationCodeGenerator.verify_code_format(code):
            return {
                "success": False,
                "message": "激活码格式不正确"
            }
        
        activation_code = self.get_activation_code(code)
        
        if not activation_code:
            return {
                "success": False,
                "message": "激活码不存在"
            }
        
        # 验证激活码
        verify_result = self.verify_activation_code(ActivationCodeVerify(code=code, user_id=user_id))
        if not verify_result["valid"]:
            return {
                "success": False,
                "message": verify_result["message"]
            }
        
        # 增加激活次数
        activation_code.current_activations += 1
        
        # 记录激活信息
        activation_record = {
            "user_id": user_id,
            "activation_time": datetime.utcnow().isoformat(),
            "device_info": device_info,
            "ip_address": ip_address
        }
        
        # 更新激活记录
        existing_records = []
        if activation_code.activation_records:
            try:
                existing_records = json.loads(activation_code.activation_records)
            except:
                existing_records = []
        
        existing_records.append(activation_record)
        activation_code.activation_records = json.dumps(existing_records)
        
        # 如果是第一次激活，设置使用时间
        if activation_code.current_activations == 1:
            activation_code.used_at = datetime.utcnow()
            activation_code.used_by = user_id
        
        # 如果达到最大激活次数，标记为已使用
        if activation_code.current_activations >= activation_code.max_activations:
            activation_code.status = ActivationCodeStatus.USED
        
        self.db.commit()
        
        return {
            "success": True,
            "message": f"激活成功，剩余激活次数: {activation_code.max_activations - activation_code.current_activations}",
            "activation_code": activation_code,
            "remaining_activations": activation_code.max_activations - activation_code.current_activations,
            "activation_record": activation_record
        }
    
    def bind_to_hardware(self, code: str, hardware_fingerprint: str, user_id: str = None) -> dict:
        """将激活码绑定到硬件"""
        activation_code = self.get_activation_code(code)
        
        if not activation_code:
            return {
                "success": False,
                "message": "激活码不存在"
            }
        
        return self.hardware_service.bind_activation_code_to_hardware(
            activation_code.id, hardware_fingerprint, user_id
        )
    
    def verify_hardware_binding(self, code: str, hardware_fingerprint: str) -> dict:
        """验证硬件绑定"""
        return self.hardware_service.verify_hardware_binding(code, hardware_fingerprint)
    
    def get_hardware_binding_info(self, code: str) -> dict:
        """获取硬件绑定信息"""
        return self.hardware_service.get_hardware_binding_info(code)
    
    def unbind_hardware(self, code: str, admin_key: str = None) -> dict:
        """解绑硬件"""
        return self.hardware_service.unbind_hardware(code, admin_key)
    
    def get_activation_codes_by_product(self, product_id: str, skip: int = 0, limit: int = 100) -> List[ActivationCode]:
        """根据产品ID获取激活码列表"""
        return self.db.query(ActivationCode)\
            .filter(ActivationCode.product_id == product_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_activation_code_stats(self, product_id: str = None) -> dict:
        """获取激活码统计信息"""
        query = self.db.query(ActivationCode)
        if product_id:
            query = query.filter(ActivationCode.product_id == product_id)
        
        total = query.count()
        unused = query.filter(ActivationCode.status == ActivationCodeStatus.UNUSED).count()
        used = query.filter(ActivationCode.status == ActivationCodeStatus.USED).count()
        expired = query.filter(ActivationCode.status == ActivationCodeStatus.EXPIRED).count()
        disabled = query.filter(ActivationCode.status == ActivationCodeStatus.DISABLED).count()
        
        return {
            "total": total,
            "unused": unused,
            "used": used,
            "expired": expired,
            "disabled": disabled
        }
    
    def get_activation_records(self, code: str) -> dict:
        """获取激活记录"""
        activation_code = self.get_activation_code(code)
        
        if not activation_code:
            return {
                "success": False,
                "message": "激活码不存在"
            }
        
        try:
            records = []
            if activation_code.activation_records:
                records = json.loads(activation_code.activation_records)
            
            return {
                "success": True,
                "activation_code": code,
                "max_activations": activation_code.max_activations,
                "current_activations": activation_code.current_activations,
                "remaining_activations": activation_code.max_activations - activation_code.current_activations,
                "records": records
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"获取激活记录失败: {str(e)}"
            }
    
    def get_code_security_info(self) -> dict:
        """获取激活码安全信息"""
        return {
            "salt_key_length": len(EnhancedActivationCodeGenerator.SALT_KEY),
            "character_set_size": len(EnhancedActivationCodeGenerator.CHARACTERS),
            "default_length": 32,
            "encryption_method": "HMAC-SHA256",
            "format_validation": True,
            "hardware_binding": True,
            "fingerprint_algorithm": "SHA256",
            "multi_activation": True
        }
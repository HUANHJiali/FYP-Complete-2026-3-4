#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT Token详细诊断脚本
用于分析JWT Token的格式和内容
"""

import jwt
import time
import base64
import json

def decode_jwt_parts(token):
    """解码JWT的三个部分"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            print("❌ JWT格式错误：应该有3个部分")
            return
        
        header_b64, payload_b64, signature_b64 = parts
        
        # 解码Header
        header = json.loads(base64.urlsafe_b64decode(header_b64 + '=' * (-len(header_b64) % 4)))
        print(f"📋 JWT Header: {json.dumps(header, indent=2)}")
        
        # 解码Payload
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + '=' * (-len(payload_b64) % 4)))
        print(f"📝 JWT Payload: {json.dumps(payload, indent=2)}")
        
        # 显示签名（前20个字符）
        print(f"🔐 JWT Signature: {signature_b64[:20]}...")
        
        return header, payload
        
    except Exception as e:
        print(f"❌ JWT解码失败: {e}")
        return None, None

def test_different_payloads():
    """测试不同的JWT payload格式"""
    
    api_key = "9697be6646e54ba08e85cc5d963201e1.7dxLq4JUSbPR84Xb"
    api_id, api_secret = api_key.split('.', 1)
    current_time = int(time.time())
    
    print("🧪 测试不同的JWT payload格式")
    print("=" * 50)
    
    # 测试不同的payload格式
    payload_formats = [
        {
            'name': '格式1: 最简单',
            'payload': {
                'api_key': api_id,
                'exp': current_time + 3600
            }
        },
        {
            'name': '格式2: 带时间戳',
            'payload': {
                'api_key': api_id,
                'exp': current_time + 3600,
                'timestamp': current_time
            }
        },
        {
            'name': '格式3: 标准JWT',
            'payload': {
                'api_key': api_id,
                'exp': current_time + 3600,
                'iat': current_time,
                'nbf': current_time
            }
        },
        {
            'name': '格式4: 智谱AI官方',
            'payload': {
                'api_key': api_id,
                'exp': current_time + 3600,
                'iat': current_time
            }
        }
    ]
    
    for format_info in payload_formats:
        print(f"\n{format_info['name']}")
        print("-" * 30)
        
        try:
            token = jwt.encode(format_info['payload'], api_secret, algorithm='HS256')
            print(f"Token: {token[:50]}...")
            
            # 验证Token
            decoded = jwt.decode(token, api_secret, algorithms=['HS256'])
            print(f"✅ 验证成功: {decoded}")
            
        except Exception as e:
            print(f"❌ 生成失败: {e}")

def check_api_key_format():
    """检查API Key格式"""
    
    api_key = "9697be6646e54ba08e85cc5d963201e1.7dxLq4JUSbPR84Xb"
    
    print("🔍 检查API Key格式")
    print("=" * 50)
    
    if '.' not in api_key:
        print("❌ API Key格式错误：缺少分隔符")
        return
    
    api_id, api_secret = api_key.split('.', 1)
    
    print(f"API ID长度: {len(api_id)}")
    print(f"API Secret长度: {len(api_secret)}")
    print(f"API ID: {api_id}")
    print(f"API Secret: {api_secret[:10]}...{api_secret[-10:]}")
    
    # 检查是否都是十六进制字符
    import re
    hex_pattern = re.compile(r'^[0-9a-fA-F]+$')
    
    if hex_pattern.match(api_id):
        print("✅ API ID格式正确（十六进制）")
    else:
        print("❌ API ID格式可能不正确")
    
    if hex_pattern.match(api_secret):
        print("✅ API Secret格式正确（十六进制）")
    else:
        print("❌ API Secret格式可能不正确")

if __name__ == "__main__":
    print("🔍 JWT Token详细诊断")
    print("=" * 60)
    
    # 检查API Key格式
    check_api_key_format()
    
    # 测试不同的payload格式
    test_different_payloads()
    
    print("\n📋 建议:")
    print("1. 检查API Key是否仍然有效")
    print("2. 确认账户有足够的调用权限")
    print("3. 尝试在智谱AI控制台中测试API Key")
    print("4. 检查账户余额和调用限制")



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智谱AI 问题诊断脚本
全面诊断智谱AI API的问题
"""

import os
import sys
import jwt
import time
import requests
import json
from datetime import datetime

def check_api_key_format(api_key):
    """检查API Key格式"""
    print("🔍 检查API Key格式...")
    
    if not api_key:
        print("❌ API Key为空")
        return False
    
    if '.' not in api_key:
        print("❌ API Key格式错误：缺少分隔符")
        return False
    
    parts = api_key.split('.')
    if len(parts) != 2:
        print("❌ API Key格式错误：应该有且仅有2个部分")
        return False
    
    api_id, api_secret = parts
    
    if len(api_id) < 10:
        print("❌ API ID长度异常")
        return False
    
    if len(api_secret) < 10:
        print("❌ API Secret长度异常")
        return False
    
    print("✅ API Key格式正确")
    print(f"  API ID: {api_id}")
    print(f"  API Secret: {api_secret[:10]}...")
    return True

def check_jwt_generation(api_key):
    """检查JWT生成"""
    print("\n🔍 检查JWT生成...")
    
    try:
        api_id, api_secret = api_key.split('.', 1)
        
        current_time = int(time.time())
        payload = {
            'api_key': api_id,
            'exp': current_time + 3600,
            'iat': current_time,
            'nbf': current_time
        }
        
        token = jwt.encode(payload, api_secret, algorithm='HS256')
        print("✅ JWT生成成功")
        print(f"  Token: {token[:50]}...")
        
        # 验证JWT
        decoded = jwt.decode(token, api_secret, algorithms=['HS256'])
        print("✅ JWT验证成功")
        print(f"  Payload: {decoded}")
        
        # 检查时间
        now = int(time.time())
        if decoded.get('iat') <= now <= decoded.get('exp'):
            print("✅ JWT时间有效")
        else:
            print("❌ JWT时间无效")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ JWT生成失败: {e}")
        return False

def test_api_endpoint(api_key, base_url, model_name):
    """测试API端点"""
    print(f"\n🧪 测试API端点: {model_name}")
    
    try:
        api_id, api_secret = api_key.split('.', 1)
        
        current_time = int(time.time())
        payload = {
            'api_key': api_id,
            'exp': current_time + 3600,
            'iat': current_time,
            'nbf': current_time
        }
        
        token = jwt.encode(payload, api_secret, algorithm='HS256')
        
        url = f"{base_url}/chat/completions"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        
        data = {
            'model': model_name,
            'messages': [
                {"role": "user", "content": "测试"}
            ],
            'max_tokens': 10
        }
        
        print(f"  URL: {url}")
        print(f"  Model: {model_name}")
        print(f"  Headers: {json.dumps(headers, indent=2)}")
        print(f"  Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"  状态码: {response.status_code}")
        print(f"  响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("  ✅ API调用成功")
            return True
        else:
            try:
                error_data = response.json()
                print(f"  ❌ API调用失败: {json.dumps(error_data, indent=2)}")
            except:
                print(f"  ❌ API调用失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ 测试异常: {e}")
        return False

def check_network_connectivity():
    """检查网络连接"""
    print("\n🔍 检查网络连接...")
    
    test_urls = [
        "https://open.bigmodel.cn",
        "https://www.baidu.com",
        "https://www.google.com"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {url}: 连接正常 (状态码: {response.status_code})")
        except Exception as e:
            print(f"❌ {url}: 连接失败 - {e}")

def main():
    """主函数"""
    print("🚀 智谱AI 问题诊断")
    print("=" * 60)
    print(f"⏰ 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 配置信息
    api_key = "fd4abef3ba11457eba10ad862d2b3ec2.PCPLHkU12JIB3aIf"
    base_url = "https://open.bigmodel.cn/api/paas/v4"
    
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"🌐 Base URL: {base_url}")
    
    # 1. 检查API Key格式
    if not check_api_key_format(api_key):
        print("\n❌ API Key格式检查失败，请检查配置")
        return
    
    # 2. 检查JWT生成
    if not check_jwt_generation(api_key):
        print("\n❌ JWT生成检查失败")
        return
    
    # 3. 检查网络连接
    check_network_connectivity()
    
    # 4. 测试API端点
    print("\n🔍 测试API端点...")
    models_to_test = ['glm-4-air', 'glm-4-flash', 'glm-4']
    
    all_failed = True
    for model in models_to_test:
        if test_api_endpoint(api_key, base_url, model):
            all_failed = False
            break
    
    # 5. 总结和建议
    print("\n" + "=" * 60)
    print("📊 诊断结果总结")
    print("=" * 60)
    
    if all_failed:
        print("❌ 所有API测试都失败")
        print("\n🔍 问题分析:")
        print("1. ✅ API Key格式正确")
        print("2. ✅ JWT生成正常")
        print("3. ❌ API调用失败")
        print("\n💡 可能的原因:")
        print("1. API Key已过期或无效")
        print("2. 账户余额不足")
        print("3. 账户没有调用权限")
        print("4. 智谱AI服务暂时不可用")
        print("\n🛠️ 建议操作:")
        print("1. 立即登录智谱AI控制台检查API Key状态")
        print("2. 确认账户余额和权限")
        print("3. 查看智谱AI控制台的调用日志")
        print("4. 联系智谱AI客服获取支持")
        print("5. 考虑创建新的API Key")
    else:
        print("✅ 找到可用的模型配置")
        print("\n🚀 系统可以正常使用")

if __name__ == "__main__":
    main()

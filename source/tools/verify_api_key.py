#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Key验证脚本
验证智谱AI API Key的有效性
"""

import os
import sys
import jwt
import time
import requests
import json

def verify_api_key(api_key):
    """验证API Key"""
    
    print("🔍 验证API Key有效性")
    print("=" * 50)
    
    if not api_key:
        print("❌ API Key为空")
        return False
    
    # 1. 检查格式
    if '.' not in api_key:
        print("❌ API Key格式错误：缺少分隔符")
        return False
    
    parts = api_key.split('.')
    if len(parts) != 2:
        print("❌ API Key格式错误：应该有且仅有2个部分")
        return False
    
    api_id, api_secret = parts
    print(f"✅ API Key格式正确")
    print(f"  API ID: {api_id}")
    print(f"  API Secret: {api_secret[:10]}...")
    
    # 2. 生成JWT
    try:
        current_time = int(time.time())
        payload = {
            'api_key': api_id,
            'exp': current_time + 3600,
            'iat': current_time,
            'nbf': current_time
        }
        
        token = jwt.encode(payload, api_secret, algorithm='HS256')
        print("✅ JWT生成成功")
        
        # 3. 测试API调用
        base_url = "https://open.bigmodel.cn/api/paas/v4"
        url = f"{base_url}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        
        # 测试最简单的请求
        data = {
            'model': 'glm-4.5-air',
            'messages': [
                {"role": "user", "content": "测试"}
            ],
            'max_tokens': 10
        }
        
        print(f"🌐 测试URL: {url}")
        print(f"🔑 测试模型: glm-4.5-air")
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API Key有效！")
            return True
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', '未知错误')
                print(f"❌ API Key无效: {error_msg}")
                
                # 分析错误原因
                if '令牌已过期' in error_msg or '验证不正确' in error_msg:
                    print("🔍 可能的原因:")
                    print("  1. API Key已过期")
                    print("  2. API Key无效")
                    print("  3. 账户余额不足")
                    print("  4. 没有调用权限")
                elif '模型不存在' in error_msg:
                    print("🔍 可能的原因:")
                    print("  1. 模型名称错误")
                    print("  2. 账户没有该模型的使用权限")
                elif '余额不足' in error_msg:
                    print("🔍 可能的原因:")
                    print("  1. 账户余额不足")
                    print("  2. 资源包未激活")
                    
            except:
                print(f"❌ API Key无效: {response.text}")
            
            return False
            
    except Exception as e:
        print(f"❌ 验证过程中发生错误: {e}")
        return False

def main():
    """主函数"""
    
    print("🚀 智谱AI API Key 验证工具")
    print("=" * 50)
    
    # 从环境变量或配置文件获取API Key
    api_key = (
        os.getenv('ZHIPUAI_API_KEY') or 
        os.getenv('OPENAI_API_KEY') or
        "fd4abef3ba11457eba10ad862d2b3ec2.PCPLHkU12JIB3aIf"  # 默认值
    )
    
    print(f"🔑 当前API Key: {api_key[:20]}...")
    print()
    
    # 验证API Key
    is_valid = verify_api_key(api_key)
    
    print("\n" + "=" * 50)
    if is_valid:
        print("🎉 API Key验证成功！")
        print("🚀 系统可以正常使用智谱AI服务")
    else:
        print("❌ API Key验证失败")
        print("\n🛠️ 建议操作:")
        print("1. 登录智谱AI控制台检查API Key状态")
        print("2. 确认新用户资源包已激活")
        print("3. 检查账户余额和权限")
        print("4. 考虑创建新的API Key")
        print("5. 联系智谱AI客服获取支持")

if __name__ == "__main__":
    main()



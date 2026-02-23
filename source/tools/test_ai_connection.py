#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智谱AI连接测试脚本
用于验证API密钥和连接是否正常
"""

import os
import requests
import json

def test_zhipuai_connection():
    """测试智谱AI连接"""
    print("🔍 开始测试智谱AI连接...")
    print("=" * 50)
    
    # 1. 检查环境变量
    print("📋 检查环境变量:")
    api_key = os.getenv('ZHIPUAI_API_KEY') or os.getenv('OPENAI_API_KEY')
    model = os.getenv('ZHIPUAI_MODEL') or os.getenv('OPENAI_MODEL')
    base_url = os.getenv('ZHIPUAI_BASE_URL') or os.getenv('OPENAI_BASE_URL')
    
    if not api_key:
        print("❌ 未找到API密钥环境变量")
        print("请运行: .\\config\\setup_zhipuai_env.ps1")
        return False
    
    print(f"✅ API密钥: {api_key[:20]}...")
    print(f"✅ 模型: {model}")
    print(f"✅ 基础URL: {base_url}")
    print()
    
    # 2. 解析API密钥
    try:
        if '.' not in api_key:
            print("❌ API密钥格式错误，缺少分隔符 '.'")
            return False
        
        api_id, api_secret = api_key.split('.', 1)
        print(f"✅ API ID: {api_id[:10]}...")
        print(f"✅ API Secret: {api_secret[:10]}...")
        print()
    except Exception as e:
        print(f"❌ 解析API密钥失败: {e}")
        return False
    
    # 3. 测试API调用 (根据智谱AI官方文档使用简单认证)
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': [
                {'role': 'user', 'content': '你好，请简单回复一下'}
            ],
            'max_tokens': 100
        }
        
        print("🚀 发送测试请求...")
        print(f"请求URL: {base_url}/chat/completions")
        print(f"请求Headers: {headers}")
        print(f"请求数据: {data}")
        print()
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"📡 响应状态码: {response.status_code}")
        print(f"📡 响应Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API调用成功！")
            print(f"📝 AI回复: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def main():
    """主函数"""
    print("🤖 智谱AI连接测试工具")
    print("=" * 50)
    
    success = test_zhipuai_connection()
    
    print()
    print("=" * 50)
    if success:
        print("🎉 测试通过！AI接口连接正常")
        print("💡 现在可以正常使用AI功能了")
    else:
        print("❌ 测试失败！请检查配置")
        print("🔧 建议检查:")
        print("   1. API密钥是否正确")
        print("   2. 账户余额是否充足")
        print("   3. 网络连接是否正常")
        print("   4. 智谱AI服务状态")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()

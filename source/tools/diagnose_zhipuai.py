#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鏅鸿氨AI 闂璇婃柇鑴氭湰
鍏ㄩ潰璇婃柇鏅鸿氨AI API鐨勯棶棰?
"""

import os
import sys
import jwt
import time
import requests
import json
from datetime import datetime

def check_api_key_format(api_key):
    """妫€鏌PI Key鏍煎紡"""
    print("馃攳 妫€鏌PI Key鏍煎紡...")
    
    if not api_key:
        print("鉂?API Key涓虹┖")
        return False
    
    if '.' not in api_key:
        print("鉂?API Key鏍煎紡閿欒锛氱己灏戝垎闅旂")
        return False
    
    parts = api_key.split('.')
    if len(parts) != 2:
        print("鉂?API Key鏍煎紡閿欒锛氬簲璇ユ湁涓斾粎鏈?涓儴鍒?)
        return False
    
    api_id, api_secret = parts
    
    if len(api_id) < 10:
        print("鉂?API ID闀垮害寮傚父")
        return False
    
    if len(api_secret) < 10:
        print("鉂?API Secret闀垮害寮傚父")
        return False
    
    print("鉁?API Key鏍煎紡姝ｇ‘")
    print(f"  API ID: {api_id}")
    print(f"  API Secret: {api_secret[:10]}...")
    return True

def check_jwt_generation(api_key):
    """妫€鏌WT鐢熸垚"""
    print("\n馃攳 妫€鏌WT鐢熸垚...")
    
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
        print("鉁?JWT鐢熸垚鎴愬姛")
        print(f"  Token: {token[:50]}...")
        
        # 楠岃瘉JWT
        decoded = jwt.decode(token, api_secret, algorithms=['HS256'])
        print("鉁?JWT楠岃瘉鎴愬姛")
        print(f"  Payload: {decoded}")
        
        # 妫€鏌ユ椂闂?
        now = int(time.time())
        if decoded.get('iat') <= now <= decoded.get('exp'):
            print("鉁?JWT鏃堕棿鏈夋晥")
        else:
            print("鉂?JWT鏃堕棿鏃犳晥")
            return False
            
        return True
        
    except Exception as e:
        print(f"鉂?JWT鐢熸垚澶辫触: {e}")
        return False

def test_api_endpoint(api_key, base_url, model_name):
    """娴嬭瘯API绔偣"""
    print(f"\n馃И 娴嬭瘯API绔偣: {model_name}")
    
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
                {"role": "user", "content": "娴嬭瘯"}
            ],
            'max_tokens': 10
        }
        
        print(f"  URL: {url}")
        print(f"  Model: {model_name}")
        print(f"  Headers: {json.dumps(headers, indent=2)}")
        print(f"  Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"  鐘舵€佺爜: {response.status_code}")
        print(f"  鍝嶅簲澶? {dict(response.headers)}")
        
        if response.status_code == 200:
            print("  鉁?API璋冪敤鎴愬姛")
            return True
        else:
            try:
                error_data = response.json()
                print(f"  鉂?API璋冪敤澶辫触: {json.dumps(error_data, indent=2)}")
            except:
                print(f"  鉂?API璋冪敤澶辫触: {response.text}")
            return False
            
    except Exception as e:
        print(f"  鉂?娴嬭瘯寮傚父: {e}")
        return False

def check_network_connectivity():
    """妫€鏌ョ綉缁滆繛鎺?""
    print("\n馃攳 妫€鏌ョ綉缁滆繛鎺?..")
    
    test_urls = [
        "https://open.bigmodel.cn",
        "https://www.baidu.com",
        "https://www.google.com"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"鉁?{url}: 杩炴帴姝ｅ父 (鐘舵€佺爜: {response.status_code})")
        except Exception as e:
            print(f"鉂?{url}: 杩炴帴澶辫触 - {e}")

def main():
    """涓诲嚱鏁?""
    print("馃殌 鏅鸿氨AI 闂璇婃柇")
    print("=" * 60)
    print(f"鈴?璇婃柇鏃堕棿: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 閰嶇疆淇℃伅
    api_key = "YOUR_ZHIPUAI_API_KEY"
    base_url = "https://open.bigmodel.cn/api/paas/v4"
    
    print(f"馃攽 API Key: {api_key[:20]}...")
    print(f"馃寪 Base URL: {base_url}")
    
    # 1. 妫€鏌PI Key鏍煎紡
    if not check_api_key_format(api_key):
        print("\n鉂?API Key鏍煎紡妫€鏌ュけ璐ワ紝璇锋鏌ラ厤缃?)
        return
    
    # 2. 妫€鏌WT鐢熸垚
    if not check_jwt_generation(api_key):
        print("\n鉂?JWT鐢熸垚妫€鏌ュけ璐?)
        return
    
    # 3. 妫€鏌ョ綉缁滆繛鎺?
    check_network_connectivity()
    
    # 4. 娴嬭瘯API绔偣
    print("\n馃攳 娴嬭瘯API绔偣...")
    models_to_test = ['glm-4-air', 'glm-4-flash', 'glm-4']
    
    all_failed = True
    for model in models_to_test:
        if test_api_endpoint(api_key, base_url, model):
            all_failed = False
            break
    
    # 5. 鎬荤粨鍜屽缓璁?
    print("\n" + "=" * 60)
    print("馃搳 璇婃柇缁撴灉鎬荤粨")
    print("=" * 60)
    
    if all_failed:
        print("鉂?鎵€鏈堿PI娴嬭瘯閮藉け璐?)
        print("\n馃攳 闂鍒嗘瀽:")
        print("1. 鉁?API Key鏍煎紡姝ｇ‘")
        print("2. 鉁?JWT鐢熸垚姝ｅ父")
        print("3. 鉂?API璋冪敤澶辫触")
        print("\n馃挕 鍙兘鐨勫師鍥?")
        print("1. API Key宸茶繃鏈熸垨鏃犳晥")
        print("2. 璐︽埛浣欓涓嶈冻")
        print("3. 璐︽埛娌℃湁璋冪敤鏉冮檺")
        print("4. 鏅鸿氨AI鏈嶅姟鏆傛椂涓嶅彲鐢?)
        print("\n馃洜锔?寤鸿鎿嶄綔:")
        print("1. 绔嬪嵆鐧诲綍鏅鸿氨AI鎺у埗鍙版鏌PI Key鐘舵€?)
        print("2. 纭璐︽埛浣欓鍜屾潈闄?)
        print("3. 鏌ョ湅鏅鸿氨AI鎺у埗鍙扮殑璋冪敤鏃ュ織")
        print("4. 鑱旂郴鏅鸿氨AI瀹㈡湇鑾峰彇鏀寔")
        print("5. 鑰冭檻鍒涘缓鏂扮殑API Key")
    else:
        print("鉁?鎵惧埌鍙敤鐨勬ā鍨嬮厤缃?)
        print("\n馃殌 绯荤粺鍙互姝ｅ父浣跨敤")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Key楠岃瘉鑴氭湰
楠岃瘉鏅鸿氨AI API Key鐨勬湁鏁堟€?
"""

import os
import sys
import jwt
import time
import requests
import json

def verify_api_key(api_key):
    """楠岃瘉API Key"""
    
    print("馃攳 楠岃瘉API Key鏈夋晥鎬?)
    print("=" * 50)
    
    if not api_key:
        print("鉂?API Key涓虹┖")
        return False
    
    # 1. 妫€鏌ユ牸寮?
    if '.' not in api_key:
        print("鉂?API Key鏍煎紡閿欒锛氱己灏戝垎闅旂")
        return False
    
    parts = api_key.split('.')
    if len(parts) != 2:
        print("鉂?API Key鏍煎紡閿欒锛氬簲璇ユ湁涓斾粎鏈?涓儴鍒?)
        return False
    
    api_id, api_secret = parts
    print(f"鉁?API Key鏍煎紡姝ｇ‘")
    print(f"  API ID: {api_id}")
    print(f"  API Secret: {api_secret[:10]}...")
    
    # 2. 鐢熸垚JWT
    try:
        current_time = int(time.time())
        payload = {
            'api_key': api_id,
            'exp': current_time + 3600,
            'iat': current_time,
            'nbf': current_time
        }
        
        token = jwt.encode(payload, api_secret, algorithm='HS256')
        print("鉁?JWT鐢熸垚鎴愬姛")
        
        # 3. 娴嬭瘯API璋冪敤
        base_url = "https://open.bigmodel.cn/api/paas/v4"
        url = f"{base_url}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        
        # 娴嬭瘯鏈€绠€鍗曠殑璇锋眰
        data = {
            'model': 'glm-4.5-air',
            'messages': [
                {"role": "user", "content": "娴嬭瘯"}
            ],
            'max_tokens': 10
        }
        
        print(f"馃寪 娴嬭瘯URL: {url}")
        print(f"馃攽 娴嬭瘯妯″瀷: glm-4.5-air")
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"馃搳 鍝嶅簲鐘舵€佺爜: {response.status_code}")
        
        if response.status_code == 200:
            print("鉁?API Key鏈夋晥锛?)
            return True
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', '鏈煡閿欒')
                print(f"鉂?API Key鏃犳晥: {error_msg}")
                
                # 鍒嗘瀽閿欒鍘熷洜
                if '浠ょ墝宸茶繃鏈? in error_msg or '楠岃瘉涓嶆纭? in error_msg:
                    print("馃攳 鍙兘鐨勫師鍥?")
                    print("  1. API Key宸茶繃鏈?)
                    print("  2. API Key鏃犳晥")
                    print("  3. 璐︽埛浣欓涓嶈冻")
                    print("  4. 娌℃湁璋冪敤鏉冮檺")
                elif '妯″瀷涓嶅瓨鍦? in error_msg:
                    print("馃攳 鍙兘鐨勫師鍥?")
                    print("  1. 妯″瀷鍚嶇О閿欒")
                    print("  2. 璐︽埛娌℃湁璇ユā鍨嬬殑浣跨敤鏉冮檺")
                elif '浣欓涓嶈冻' in error_msg:
                    print("馃攳 鍙兘鐨勫師鍥?")
                    print("  1. 璐︽埛浣欓涓嶈冻")
                    print("  2. 璧勬簮鍖呮湭婵€娲?)
                    
            except:
                print(f"鉂?API Key鏃犳晥: {response.text}")
            
            return False
            
    except Exception as e:
        print(f"鉂?楠岃瘉杩囩▼涓彂鐢熼敊璇? {e}")
        return False

def main():
    """涓诲嚱鏁?""
    
    print("馃殌 鏅鸿氨AI API Key 楠岃瘉宸ュ叿")
    print("=" * 50)
    
    # 浠庣幆澧冨彉閲忔垨閰嶇疆鏂囦欢鑾峰彇API Key
    api_key = (
        os.getenv('ZHIPUAI_API_KEY') or 
        os.getenv('OPENAI_API_KEY') or
        "YOUR_ZHIPUAI_API_KEY"  # 榛樿鍊?
    )
    
    print(f"馃攽 褰撳墠API Key: {api_key[:20]}...")
    print()
    
    # 楠岃瘉API Key
    is_valid = verify_api_key(api_key)
    
    print("\n" + "=" * 50)
    if is_valid:
        print("馃帀 API Key楠岃瘉鎴愬姛锛?)
        print("馃殌 绯荤粺鍙互姝ｅ父浣跨敤鏅鸿氨AI鏈嶅姟")
    else:
        print("鉂?API Key楠岃瘉澶辫触")
        print("\n馃洜锔?寤鸿鎿嶄綔:")
        print("1. 鐧诲綍鏅鸿氨AI鎺у埗鍙版鏌PI Key鐘舵€?)
        print("2. 纭鏂扮敤鎴疯祫婧愬寘宸叉縺娲?)
        print("3. 妫€鏌ヨ处鎴蜂綑棰濆拰鏉冮檺")
        print("4. 鑰冭檻鍒涘缓鏂扮殑API Key")
        print("5. 鑱旂郴鏅鸿氨AI瀹㈡湇鑾峰彇鏀寔")

if __name__ == "__main__":
    main()




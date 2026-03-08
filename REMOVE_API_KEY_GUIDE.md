# 绉婚櫎纭紪鐮丄PI瀵嗛挜 - 璇︾粏姝ラ鎸囧崡

**鐩爣**: 灏哾ocker-compose.yml涓殑纭紪鐮丄PI瀵嗛挜绉诲埌鐜鍙橀噺涓?

**瀹夊叏椋庨櫓**: 馃敶 楂?- API瀵嗛挜鏆撮湶鍦ㄤ唬鐮佷腑鍙兘琚互鐢?

---

## 馃搵 鎿嶄綔姝ラ

### 姝ラ1: 澶囦唤褰撳墠閰嶇疆 鉁?

```bash
# 澶囦唤docker-compose.yml
copy docker-compose.yml docker-compose.yml.backup
```

鎴栬€呮墜鍔ㄥ浠斤細
- 鎵撳紑 `docker-compose.yml`
- 鍙﹀瓨涓?`docker-compose.yml.backup`

---

### 姝ラ2: 淇敼docker-compose.yml 鉁?

**鎵惧埌绗?8琛?*锛?
```yaml
ZHIPUAI_API_KEY: YOUR_ZHIPUAI_API_KEY
```

**淇敼涓?*锛?
```yaml
ZHIPUAI_API_KEY: ${ZHIPUAI_API_KEY}
```

**瀹屾暣鐨勭幆澧冨彉閲忛儴鍒嗗簲璇ュ涓?*锛?
```yaml
environment:
      # 3. 鍙傝€?.env.production.example 鏂囦欢
      SECRET_KEY: django-insecure-bh^5636f!$(au7fy^nzn()6*4ht974p(&pzcd&9z_**=t%^+^4
      DEBUG: "True"  # 鈿狅笍 鐢熶骇鐜鏀逛负 "False"
      ALLOWED_HOSTS: localhost,127.0.0.1,0.0.0.0,backend  # 鈿狅笍 鐢熶骇鐜鏀逛负瀹為檯鍩熷悕
      # CORS 閰嶇疆
      CORS_ALLOWED_ORIGINS: http://localhost:8080,http://127.0.0.1:8080
      CSRF_TRUSTED_ORIGINS: http://localhost:8080,http://127.0.0.1:8080
      # AI 閰嶇疆锛堝彲閫夛級
      ZHIPUAI_API_KEY: ${ZHIPUAI_API_KEY}  # 鉁?淇敼杩欎竴琛?
      ZHIPUAI_MODEL: glm-4-flash
      ZHIPUAI_BASE_URL: https://open.bigbigmodel.cn/api/paas/v4
```

---

### 姝ラ3: 鏇存柊.env鏂囦欢 鉁?

**鎵撳紑`.env`鏂囦欢**锛?
```bash
notepad .env
```

**鎵惧埌杩欎竴琛?*锛堢14琛岋級锛?
```
ZHIPUAI_API_KEY=your_api_key_here
```

**鏇挎崲涓轰綘鐨勭湡瀹濧PI瀵嗛挜**锛?
```
ZHIPUAI_API_KEY=YOUR_ZHIPUAI_API_KEY
```

鎴栬€呭鏋滀綘鎯充娇鐢ㄤ竴涓柊鐨凙PI瀵嗛挜锛屾浛鎹负浣犱粠ZhipuAI鑾峰彇鐨勬柊瀵嗛挜銆?

**淇濆瓨鏂囦欢** (Ctrl+S)

---

### 姝ラ4: 閲嶅惎Docker鏈嶅姟 鉁?

#### Windows PowerShell:
```bash
# 鍋滄鏈嶅姟
docker-compose down

# 閲嶆柊鍚姩
docker-compose up -d
```

#### Windows Git Bash:
```bash
docker-compose down
docker-compose up -d
```

#### Linux/Mac:
```bash
sudo docker-compose down
sudo docker-compose up -d
```

---

### 姝ラ5: 楠岃瘉淇 鉁?

**妫€鏌ョ幆澧冨彉閲忔槸鍚﹀姞杞?*锛?
```bash
docker-compose exec backend env | grep ZHIPUAI
```

搴旇鐪嬪埌锛?
```
ZHIPUAI_API_KEY=YOUR_ZHIPUAI_API_KEY
```

**娴嬭瘯API鍔熻兘**锛?
1. 鐧诲綍绯荤粺
2. 灏濊瘯浣跨敤AI鍔熻兘锛堝鏅鸿兘璇勫垎鎴栭鐩敓鎴愶級
3. 纭鍔熻兘姝ｅ父宸ヤ綔

---

## 馃攳 楠岃瘉鏂规硶

### 娴嬭瘯1: 妫€鏌ュ鍣ㄧ幆澧冨彉閲?
```bash
docker-compose exec backend printenv | grep ZHIPUAI
```

**鏈熸湜杈撳嚭**:
```
ZHIPUAI_API_KEY=浣犵殑API瀵嗛挜
ZHIPUAI_MODEL=glm-4-flash
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

### 娴嬭瘯2: 鍚庣鏃ュ織妫€鏌?
```bash
docker logs fyp_backend --tail 50
```

鏌ョ湅鏄惁鏈堿PI瀵嗛挜鐩稿叧鐨勯敊璇俊鎭€?

### 娴嬭瘯3: 鍔熻兘楠岃瘉
```bash
# 璁块棶鍓嶇
start http://localhost:8080

# 鐧诲綍骞舵祴璇旳I鍔熻兘
```

---

## 鈿狅笍 甯歌闂

### Q1: 淇敼鍚嶢PI涓嶅伐浣滐紵
**A**: 妫€鏌ヤ互涓嬪嚑鐐癸細
1. `.env`鏂囦欢涓殑API瀵嗛挜鏄惁姝ｇ‘
2. docker-compose.yml鏄惁姝ｇ‘淇敼
3. 鏈嶅姟鏄惁宸查噸鍚?

### Q2: 濡備綍鑾峰彇鏂扮殑API瀵嗛挜锛?
**A**: 璁块棶 [ZhipuAI寮€鏀惧钩鍙癩(https://open.bigmodel.cn/)锛?
1. 娉ㄥ唽/鐧诲綍璐﹀彿
2. 杩涘叆"API瀵嗛挜绠＄悊"
3. 鍒涘缓鏂扮殑API瀵嗛挜
4. 澶嶅埗瀵嗛挜骞舵洿鏂板埌`.env`鏂囦欢

### Q3: 鍙互涓嶄娇鐢ˋPI瀵嗛挜鍚楋紵
**A**: 濡傛灉涓嶄娇鐢ˋI鍔熻兘锛屽彲浠ワ細
- 涓存椂娉ㄩ噴鎺塦.env`涓殑API瀵嗛挜琛?
- 鎴栧湪docker-compose.yml涓敞閲婃帀鐩稿叧閰嶇疆

### Q4: 瀵嗛挜浼氳鎻愪氦鍒癎it鍚楋紵
**A**: 涓嶄細锛乣.env`鏂囦欢宸插湪`.gitignore`涓紝涓嶄細琚彁浜わ細
```bash
# .gitignore 鍖呭惈:
.env
```

---

## 馃摑 瀹夊叏鏈€浣冲疄璺?

### 鉁?鎺ㄨ崘鍋氭硶

1. **姘歌繙涓嶈鎻愪氦`.env`鏂囦欢鍒癎it**
2. 浣跨敤涓嶅悓鐨凙PI瀵嗛挜鐢ㄤ簬寮€鍙?娴嬭瘯/鐢熶骇
3. 瀹氭湡杞崲API瀵嗛挜
4. 涓轰笉鍚岄」鐩娇鐢ㄤ笉鍚岀殑瀵嗛挜
5. 璁剧疆API瀵嗛挜鐨勪娇鐢ㄩ檺棰?

### 鉂?閬垮厤鐨勫仛娉?

1. 鉂?鍦ㄤ唬鐮佷腑纭紪鐮佸瘑閽?
2. 鉂?鍦ㄥ叕寮€鐨勬枃妗ｄ腑鍖呭惈瀵嗛挜
3. 鉂?鍦ㄨ亰澶╄褰曚腑鍒嗕韩瀵嗛挜
4. 鉂?浣跨敤榛樿鎴栫ず渚嬪瘑閽?

---

## 馃幆 蹇€熷弬鑰?

### 淇敼鍓嶅悗瀵规瘮

**淇敼鍓?* 鉂?
```yaml
environment:
  - ZHIPUAI_API_KEY: YOUR_ZHIPUAI_API_KEY
```

**淇敼鍚?* 鉁?
```yaml
environment:
  - ZHIPUAI_API_KEY: ${ZHIPUAI_API_KEY}
```

### .env鏂囦欢閰嶇疆

```bash
# 鏁版嵁搴撻厤缃?
DB_NAME=db_exam
DB_USER=root
DB_PASSWORD=123456
DB_HOST=127.0.0.1
DB_PORT=3306

# Django閰嶇疆
SECRET_KEY=django-insecure-please-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ZhipuAI閰嶇疆
ZHIPUAI_API_KEY=YOUR_ZHIPUAI_API_KEY
ZHIPUAI_MODEL=glm-4-flash
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

---

## 馃殌 瀹屾暣鎿嶄綔娴佺▼

### 涓€閿墽琛岋紙鎺ㄨ崘锛?

```bash
# 1. 澶囦唤
copy docker-compose.yml docker-compose.yml.backup

# 2. 淇敼.env鏂囦欢
notepad .env
# 鏇存柊 ZHIPUAI_API_KEY=浣犵殑瀵嗛挜

# 3. 閲嶅惎鏈嶅姟
docker-compose restart backend

# 4. 楠岃瘉
docker-compose exec backend env | grep ZHIPUAI
```

### 鍒嗘鎵ц

```bash
# 姝ラ1: 澶囦唤
docker-compose.yml.backup
```

```bash
# 姝ラ2: 缂栬緫docker-compose.yml
# 鎵惧埌绗?8琛岋紝灏?
# ZHIPUAI_API_KEY: YOUR_ZHIPUAI_API_KEY
# 鏀逛负:
# ZHIPUAI_API_KEY: ${ZHIPUAI_API_KEY}
```

```bash
# 姝ラ3: 缂栬緫.env鏂囦欢
notepad .env
# 纭繚 ZHIPUAI_API_KEY 鏈夋纭殑鍊?
```

```bash
# 姝ラ4: 閲嶅惎
docker-compose restart backend
```

---

## 鉁?楠岃瘉鎴愬姛鏍囧織

淇鎴愬姛鍚庯紝浣犲簲璇ョ湅鍒帮細

1. 鉁?`docker-compose.yml`绗?8琛屾樉绀? `ZHIPUAI_API_KEY: ${ZHIPUAI_API_KEY}`
2. 鉁?`.env`鏂囦欢鍖呭惈浣犵殑鐪熷疄API瀵嗛挜
3. 鉁?`docker exec`鍛戒护鑳芥纭樉绀虹幆澧冨彉閲?
4. 鉁?AI鍔熻兘姝ｅ父宸ヤ綔

---

## 馃摓 闇€瑕佸府鍔╋紵

濡傛灉閬囧埌闂锛?

1. **鏌ョ湅璇︾粏鎶ュ憡**: `notepad IMPROVEMENT_REPORT_*.md`
2. **鏌ョ湅淇鎸囧崡**: `notepad fixes/api_key_fix.md`
3. **妫€鏌ユ湇鍔℃棩蹇?*: `docker logs fyp_backend`

---

**閲嶈鎻愮ず**:
- 鉁?淇敼鍓嶅厛澶囦唤
- 鉁?鍦ㄦ祴璇曠幆澧冮獙璇佸悗鍐嶅簲鐢ㄥ埌鐢熶骇
- 鉁?涓嶈鍦ㄥ叕鍏卞満鍚堟毚闇睞PI瀵嗛挜
- 鉁?瀹氭湡杞崲瀵嗛挜浠ユ彁楂樺畨鍏ㄦ€?

**瀹屾垚杩欎簺姝ラ鍚庯紝浣犵殑API瀵嗛挜灏卞畨鍏ㄤ簡锛?* 馃敀


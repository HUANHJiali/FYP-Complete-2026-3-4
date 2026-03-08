# FYP椤圭洰鑷姩鏀硅繘浣跨敤鎸囧崡

## 馃幆 绠€浠?

杩欐槸涓€涓嚜鍔ㄥ寲鐨凢YP椤圭洰鏀硅繘宸ュ叿闆嗭紝鍙互锛?
- 馃攳 鑷姩妫€娴嬪畨鍏ㄥ拰鎬ц兘闂
- 馃敡 鐢熸垚淇鏂规鍜岃剼鏈?
- 馃搳 鎻愪緵璇︾粏鐨勬敼杩涘缓璁?
- 馃摑 鍒涘缓瀹屾暣鐨勬敼杩涙姤鍛?

---

## 馃殌 蹇€熷紑濮?

### 鏂规硶1: 浣跨敤Python鑴氭湰锛堟帹鑽愶級

```bash
# Windows
python auto_fix.py

# Linux/Mac
python3 auto_fix.py
```

### 鏂规硶2: 浣跨敤Bash鑴氭湰

```bash
# Linux/Mac
chmod +x auto_fix.sh
./auto_fix.sh

# Git Bash (Windows)
bash auto_fix.sh
```

---

## 馃搵 宸ュ叿鍔熻兘

### 1. 鑷姩妫€鏌ュ姛鑳?

鉁?**XSS婕忔礊妫€娴?*
- 鎵弿鍓嶇浠ｇ爜涓殑`v-html`浣跨敤
- 璇嗗埆鐩存帴娓叉煋鐢ㄦ埛杈撳叆鐨勯闄?
- 鐢熸垚瀹夊叏鐨勪慨澶嶆柟妗?

鉁?**鏁忔劅淇℃伅妫€娴?*
- 妫€鏌ョ‖缂栫爜鐨凙PI瀵嗛挜
- 鎵弿閰嶇疆鏂囦欢涓殑鏁忔劅淇℃伅
- 鎻愪緵瀹夊叏瀛樺偍鏂规

鉁?**瀵嗙爜瀛楁妫€鏌?*
- 楠岃瘉瀵嗙爜瀛楁闀垮害鏄惁瓒冲
- 妫€娴嬪彲鑳界殑瀵嗙爜鎴柇椋庨櫓
- 鐢熸垚鏁版嵁搴撲慨澶嶈剼鏈?

鉁?**浠ｇ爜璐ㄩ噺鍒嗘瀽**
- 妫€鏌ヤ唬鐮佸鏉傚害
- 璇嗗埆閲嶅浠ｇ爜妯″紡
- 鎻愪緵浼樺寲寤鸿

鉁?**瀹夊叏鎵弿**
- 妫€娴婦EBUG妯″紡寮€鍚?
- 璇嗗埆纭紪鐮佸瘑鐮?
- 鎵弿SQL娉ㄥ叆椋庨櫓

---

## 馃搳 鐢熸垚鐨勬枃浠?

杩愯鍚庝細鐢熸垚浠ヤ笅鏂囦欢锛?

### 1. 鏀硅繘鎶ュ憡
```
IMPROVEMENT_REPORT_20260208_183000.md
```
- 鍙戠幇鐨勯棶棰樺垪琛?
- 淇鏂规璇存槑
- 涓嬩竴姝ヨ鍔ㄥ缓璁?

### 2. 淇鏂囦欢
```
fixes/
鈹溾攢鈹€ xss_fix_messageCenter.vue    # XSS婕忔礊淇
鈹溾攢鈹€ api_key_fix.md                 # API瀵嗛挜淇鎸囧崡
鈹斺攢鈹€ fix_password_length.py        # 瀵嗙爜瀛楁淇鑴氭湰
```

### 3. 閰嶇疆鏂囦欢
```
.env                              # 鐜鍙橀噺妯℃澘
```

---

## 馃敡 浣跨敤淇鏂规

### XSS婕忔礊淇

**鏌ョ湅淇鏂规**:
```bash
cat fixes/xss_fix_messageCenter.vue
```

**鎵嬪姩搴旂敤淇**:
```bash
# 鏂规硶1: 鐩存帴鏇挎崲
cp fixes/xss_fix_messageCenter.vue source/client/src/views/pages/messageCenter.vue

# 鏂规硶2: 鎵嬪姩缂栬緫
# 鎵撳紑 source/client/src/views/pages/messageCenter.vue
# 鎵惧埌绗?64琛?
# 灏? v-html="formatContent(selectedMessage.content)"
# 鏀逛负: {{ selectedMessage.content }}
```

### API瀵嗛挜淇

**1. 鏌ョ湅`.env`鏂囦欢**:
```bash
cat .env
```

**2. 鏇存柊API瀵嗛挜**:
```bash
# 缂栬緫.env鏂囦欢锛屽皢your_api_key_here鏇挎崲涓虹湡瀹炲瘑閽?
notepad .env  # Windows
vim .env      # Linux/Mac
```

**3. 淇敼`docker-compose.yml`**:
```yaml
# 鎵惧埌杩欎竴琛?
environment:
  - ZHIPUAI_API_KEY=YOUR_ZHIPUAI_API_KEY

# 鏀逛负:
environment:
  - ZHIPUAI_API_KEY=${ZHIPUAI_API_KEY}
```

**4. 閲嶅惎鏈嶅姟**:
```bash
docker-compose down
docker-compose up -d
```

### 瀵嗙爜瀛楁淇

**杩愯淇鑴氭湰**:
```bash
python fixes/fix_password_length.py
```

**楠岃瘉淇**:
```bash
# 妫€鏌ュ瘑鐮佹槸鍚﹀彲鐢?
docker exec fyp_mysql mysql -uroot -p123456 db_exam -e "DESCRIBE fater_users;"
```

---

## 馃搱 鏀硅繘浼樺厛绾?

### 馃敶 绔嬪嵆淇锛?澶╁唴锛?

1. 鉁?**XSS婕忔礊** - 瀹夊叏椋庨櫓楂?
2. 鉁?**API瀵嗛挜娉勯湶** - 鍙兘瀵艰嚧瀵嗛挜婊ョ敤
3. 鉁?**瀵嗙爜瀛楁** - 鍙兘瀵艰嚧瀵嗙爜鎴柇

### 馃煛 杩戞湡淇锛?鍛ㄥ唴锛?

4. 鈴?**N+1鏌ヨ** - 鎬ц兘闂
5. 鈴?**閿欒澶勭悊** - 浠ｇ爜璐ㄩ噺
6. 鈴?**鏃ュ織璁板綍** - 鍙淮鎶ゆ€?

### 馃煝 闀挎湡鏀硅繘锛?涓湀鍐咃級

7. 鈴?**API鏂囨。** - 寮€鍙戜綋楠?
8. 鈴?**娴嬭瘯瑕嗙洊** - 浠ｇ爜璐ㄩ噺
9. 鈴?**绉诲姩绔?* - 鐢ㄦ埛浣撻獙

---

## 馃幆 瀹屾暣鐨勬敼杩涜鍒?

鏌ョ湅璇︾粏鐨勬敼杩涜鍒掞細
```bash
cat AUTO_IMPROVEMENT_PLAN.md
```

鍖呮嫭锛?
- 闂璇︾粏鍒嗘瀽
- 淇鏂规璇存槑
- 宸ヤ綔閲忎及绠?
- 瀹炴柦姝ラ

---

## 馃攧 鎸佺画鏀硅繘

### 瀹氭湡杩愯妫€鏌?

寤鸿姣忓懆杩愯涓€娆¤嚜鍔ㄦ鏌ワ細
```bash
# Windows
python auto_fix.py

# Linux/Mac
python3 auto_fix.py
```

### Git宸ヤ綔娴佸缓璁?

```bash
# 1. 鍒涘缓鏀硅繘鍒嗘敮
git checkout -b improvement/security-fix

# 2. 杩愯鑷姩妫€鏌?
python auto_fix.py

# 3. 搴旂敤淇
# 锛堟牴鎹姤鍛婃墜鍔ㄥ簲鐢ㄤ慨澶嶏級

# 4. 娴嬭瘯
npm run test  # 鍓嶇娴嬭瘯
python manage.py test  # 鍚庣娴嬭瘯

# 5. 鎻愪氦
git add .
git commit -m "淇瀹夊叏闂锛歑SS婕忔礊鍜孉PI瀵嗛挜"

# 6. 鍚堝苟
git checkout main
git merge improvement/security-fix
```

---

## 馃摓 鑾峰彇甯姪

### 鏌ョ湅甯姪
```bash
python auto_fix.py --help
```

### 鏌ョ湅鐢熸垚鐨勬姤鍛?
```bash
# 鏌ョ湅鏈€鏂版姤鍛?
cat IMPROVEMENT_REPORT_*.md | more

# 鎴栬€呭湪缂栬緫鍣ㄤ腑鎵撳紑
notepad IMPROVEMENT_REPORT_*.md  # Windows
vim IMPROVEMENT_REPORT_*.md     # Linux/Mac
```

---

## 鈿狅笍 娉ㄦ剰浜嬮」

### 杩愯鍓嶅噯澶?

1. 鉁?**纭繚鍦ㄩ」鐩牴鐩綍**
   ```bash
   cd D:\涓嬭浇\FYP2025-12-27-main
   ```

2. 鉁?**澶囦唤褰撳墠浠ｇ爜**
   ```bash
   git add .
   git commit -m "鑷姩鏀硅繘鍓嶇殑澶囦唤"
   ```

3. 鉁?**鍒涘缓鏀硅繘鍒嗘敮**锛堟帹鑽愶級
   ```bash
   git checkout -b improvement/auto-fix
   ```

### 搴旂敤淇鍓?

1. 鈿狅笍 **浠旂粏闃呰鏀硅繘鎶ュ憡**
2. 鈿狅笍 **鍦ㄦ祴璇曠幆澧冨厛楠岃瘉**
3. 鈿狅笍 **澶囦唤閲嶈鏁版嵁**

### 搴旂敤淇鍚?

1. 鉁?**杩愯娴嬭瘯纭繚鏃犲洖褰?*
2. 鉁?**妫€鏌ュ墠鍚庣鍔熻兘姝ｅ父**
3. 鉁?**鎻愪氦Git骞剁紪鍐欐竻鏅扮殑commit message**

---

## 馃摎 鐩稿叧鏂囨。

- `AUTO_IMPROVEMENT_PLAN.md` - 璇︾粏鏀硅繘璁″垝
- `瀛︾敓鍔熻兘瀹屾暣娴嬭瘯鎶ュ憡.md` - 鍔熻兘娴嬭瘯鎶ュ憡
- `涓枃涔辩爜闂淇鎶ュ憡.md` - 缂栫爜闂淇

---

## 馃帀 鎬荤粨

杩欎釜鑷姩鍖栧伐鍏峰彲浠ュ府鍔╀綘锛?
- 鉁?蹇€熻瘑鍒畨鍏ㄩ棶棰?
- 鉁?鎻愪緵璇︾粏鐨勪慨澶嶆柟妗?
- 鉁?鐢熸垚瀹屾暣鐨勬敼杩涙姤鍛?
- 鉁?璺熻釜鏀硅繘杩涘害

**寤鸿鐨勫伐浣滄祦绋?*:
1. 姣忓懆杩愯涓€娆¤嚜鍔ㄦ鏌?
2. 鎸変紭鍏堢骇淇鍙戠幇鐨勯棶棰?
3. 鎸佺画鏀硅繘浠ｇ爜璐ㄩ噺
4. 淇濇寔瀹夊叏鎬у拰鎬ц兘浼樺寲

寮€濮嬩娇鐢細
```bash
python auto_fix.py
```

---

**鐢熸垚鏃堕棿**: 2026-02-08
**鐗堟湰**: v1.0
**鐘舵€?*: 鉁?鍙敤


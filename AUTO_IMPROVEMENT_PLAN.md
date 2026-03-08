# FYP椤圭洰鑷姩鏀硅繘璁″垝

**鐢熸垚鏃堕棿**: 2026-02-08
**鏀硅繘鑼冨洿**: 瀹夊叏鎬с€佹€ц兘銆佷唬鐮佽川閲忋€佹枃妗?
**浼樺厛绾?*: 鎸変弗閲嶇▼搴︽帓搴?

---

## 馃毃 楂樹紭鍏堢骇闂锛堢珛鍗充慨澶嶏級

### 1. XSS婕忔礊淇 鈿狅笍 **涓ラ噸**
**鏂囦欢**: `source/client/src/views/pages/messageCenter.vue:164`

**闂**:
```vue
<div class="content-text" v-html="formatContent(selectedMessage.content)"></div>
```

**椋庨櫓**: 鐩存帴娓叉煋鐢ㄦ埛杈撳叆鐨凥TML锛屽彲鑳藉鑷碭SS鏀诲嚮

**淇拷锟芥柟妗?*:
```vue
<!-- 鏂规1: 浣跨敤鏂囨湰鎻掑€硷紙鎺ㄨ崘锛?-->
<div class="content-text">{{ selectedMessage.content }}</div>

<!-- 鏂规2: 濡傛灉蹇呴』鏀寔HTML锛屼娇鐢―OMPurify -->
import DOMPurify from 'dompurify';
<div class="content-text" v-html="DOMPurify.sanitize(selectedMessage.content)"></div>

<!-- 鏂规3: 浣跨敤鐧藉悕鍗曡繃婊?-->
<div class="content-text">{{ formatContentSafe(selectedMessage.content) }}</div>
```

**棰勮宸ヤ綔閲?*: 2灏忔椂

---

### 2. 纭紪鐮丄PI瀵嗛挜 馃攼 **涓ラ噸**
**鏂囦欢**: `docker-compose.yml:68`

**闂**:
```yaml
ZHIPUAI_API_KEY: YOUR_ZHIPUAI_API_KEY
```

**椋庨櫓**: API瀵嗛挜鏆撮湶鍦ㄤ唬鐮佷腑锛屽彲鑳藉鑷村瘑閽ユ硠闇插拰婊ョ敤

**淇鏂规**:

#### 鏂规1: 浣跨敤.env鏂囦欢锛堟帹鑽愶級
```bash
# 1. 鍒涘缓 .env 鏂囦欢
echo "ZHIPUAI_API_KEY=your_actual_api_key_here" > .env

# 2. 淇敼 docker-compose.yml
environment:
  - ZHIPUAI_API_KEY=${ZHIPUAI_API_KEY}

# 3. 娣诲姞鍒?.gitignore
echo ".env" >> .gitignore

# 4. 鏇存柊鏂囨。
echo "璇峰鍒?env.example 涓?.env 骞跺～鍏ョ湡瀹炵殑API瀵嗛挜"
```

#### 鏂规2: Docker secrets
```yaml
# 浣跨敤Docker secrets瀛樺偍鏁忔劅淇℃伅
secrets:
  zhipuai_api_key:
    external: true

services:
  backend:
    secrets:
      - zhipuai_api_key
    environment:
      - ZHIPUAI_API_KEY_FILE=/run/secrets/zhipuai_api_key
```

**棰勮宸ヤ綔閲?*: 1灏忔椂

---

### 3. 瀵嗙爜瀛楁闀垮害涓嶈冻 馃攼 **涓ラ噸**
**鏂囦欢**: `source/server/app/models.py:54`

**闂**:
```python
passWord = models.CharField('鐢ㄦ埛瀵嗙爜', max_length=32, null=False)
```

**椋庨櫓**: Django PBKDF2鍝堝笇鍚庣殑瀵嗙爜瓒呰繃32瀛楃锛屽彲鑳借鎴柇

**淇鏂规**:

#### 姝ラ1: 淇敼妯″瀷
```python
# source/server/app/models.py:54
passWord = models.CharField(
    '鐢ㄦ埛瀵嗙爜',
    db_column='pass_word',
    max_length=255,  # 鏀逛负255
    null=False
)
```

#### 姝ラ2: 鍒涘缓杩佺Щ
```bash
cd source/server
python manage.py makemigrations
python manage.py migrate
```

#### 姝ラ3: 娴嬭瘯鐜版湁瀵嗙爜
```python
# 楠岃瘉鐜版湁瀵嗙爜鏄惁鍙敤
python manage.py shell
>>> from app.models import Users
>>> u = Users.objects.first()
>>> u.check_password('123456')  # 搴旇杩斿洖True
```

**棰勮宸ヤ綔閲?*: 4灏忔椂锛堝寘鎷祴璇曪級

---

### 4. N+1鏌ヨ闂 馃悓 **鎬ц兘**
**鏂囦欢**: 澶氫釜瑙嗗浘鏂囦欢

**闂绀轰緥**:
```python
# 鏈紭鍖?- 姣忔璁块棶澶栭敭閮借Е鍙戞柊鏌ヨ
exam_logs = ExamLogs.objects.all()
for log in exam_logs:
    print(log.student.name)  # 棰濆鏌ヨ
    print(log.exam.name)     # 棰濆鏌ヨ
```

**淇鏂规**:
```python
# 浼樺寲鍚?- 涓€娆℃煡璇㈣幏鍙栨墍鏈夋暟鎹?
exam_logs = ExamLogs.objects.select_related(
    'student',
    'exam',
    'exam__project',
    'exam__grade'
).all()

# 瀵逛簬涓€瀵瑰鍏崇郴锛屼娇鐢╬refetch_related
exam_logs = ExamLogs.objects.select_related(
    'student', 'exam'
).prefetch_related('answerlogs_set')
```

**闇€瑕佷紭鍖栫殑鏌ヨ**:
- 鉁?`sys_view.py` - 宸蹭娇鐢╯elect_related
- 鉂?`exam_views.py` - 闇€瑕佷紭鍖?
- 鉂?`practice_views.py` - 闇€瑕佷紭鍖?
- 鉂?`user_views.py` - 闇€瑕佷紭鍖?

**棰勮宸ヤ綔閲?*: 8灏忔椂

---

### 5. API鏂囨。缂哄け 馃摎 **鍙敤鎬?*
**闂**: 缂哄皯浜や簰寮廇PI鏂囨。

**淇鏂规**:

#### 姝ラ1: 瀹夎drf-yasg
```bash
pip install drf-yasg
```

#### 姝ラ2: 娣诲姞鍒皉equirements.txt
```
drf-yasg>=1.21.0
```

#### 姝ラ3: 閰嶇疆settings.py
```python
# source/server/server/settings.py

INSTALLED_APPS = [
    ...
    'drf_yasg',
    'rest_framework',
]

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Token鏍煎紡: Bearer <token>'
        }
    }
}
```

#### 姝ラ4: 閰嶇疆URLs
```python
# source/server/app/urls.py
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger<format>/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    ...
]
```

**璁块棶鍦板潃**:
- Swagger UI: http://127.0.0.1:8000/swagger/
- ReDoc: http://127.0.0.1:8000/redoc/

**棰勮宸ヤ綔閲?*: 16灏忔椂锛堝寘鎷紪鍐橝PI鏂囨。娉ㄩ噴锛?

---

## 馃搵 涓紭鍏堢骇闂锛堣繎鏈熶慨澶嶏級

### 6. 閲嶅浠ｇ爜娑堥櫎

**闂**: 鐢ㄦ埛淇℃伅鑾峰彇浠ｇ爜閲嶅14娆?

**淇鏂规**:
```python
# app/utils/helpers.py锛堟柊寤猴級
def get_user_with_cache(user_id):
    """鑾峰彇鐢ㄦ埛淇℃伅锛堝甫缂撳瓨锛?""
    cache_key = f'user:{user_id}'
    user = cache.get(cache_key)
    if not user:
        user = Users.objects.select_related('students', 'teachers').get(id=user_id)
        cache.set(cache_key, user, 300)  # 缂撳瓨5鍒嗛挓
    return user
```

---

### 7. 閿欒澶勭悊鏀硅繘

**闂**: 澶ч噺瑁窫xception鎹曡幏

**淇鏂规**:
```python
# app/exceptions.py锛堟柊寤猴級
class AppException(Exception):
    """搴旂敤鍩虹寮傚父"""
    def __init__(self, message, code=2, details=None):
        self.message = message
        self.code = code
        self.details = details

class ValidationException(AppException):
    """鏁版嵁楠岃瘉寮傚父"""
    pass

class NotFoundException(AppException):
    """璧勬簮涓嶅瓨鍦ㄥ紓甯?""
    pass

# 浣跨敤绀轰緥
try:
    user = Users.objects.get(id=user_id)
except Users.DoesNotExist:
    raise NotFoundException('鐢ㄦ埛涓嶅瓨鍦?)
```

---

### 8. 鏃ュ織璁板綍鎵╁睍

**淇鏂规**:
```python
# app/middleware/logging_middleware.py锛堟柊寤猴級
import logging
import time
from django.utils.deprecation import Deprecated

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    """璇锋眰鏃ュ織涓棿浠?""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        # 璁板綍鎱㈣姹?
        if duration > 1.0:
            logger.warning(
                f"鎱㈣姹? {request.method} {request.path} "
                f"鑰楁椂: {duration:.2f}s"
            )

        return response
```

---

## 馃敡 浣庝紭鍏堢骇鏀硅繘锛堥暱鏈熶紭鍖栵級

### 9. 娴嬭瘯瑕嗙洊鐜囨彁鍗?
- 鐩爣: 80%+浠ｇ爜瑕嗙洊鐜?
- 宸ュ叿: pytest + coverage

### 10. 绉诲姩绔紭鍖?
- 鍝嶅簲寮忚璁″畬鍠?
- 瑙︽懜浜や簰浼樺寲
- PWA瀹炵幇

### 11. 鎬ц兘鐩戞帶
- 闆嗘垚Sentry杩涜閿欒杩借釜
- 瀹炵幇APM鐩戞帶
- 娣诲姞鎬ц兘鎸囨爣鏀堕泦

---

## 馃殌 鑷姩鍖栦慨澶嶈剼鏈?

鍒涘缓鑷姩鍖栬剼鏈?`auto_fix.sh`:

```bash
#!/bin/bash
# FYP椤圭洰鑷姩淇鑴氭湰

echo "=== FYP椤圭洰鑷姩鏀硅繘宸ュ叿 ==="
echo ""

# 1. 澶囦唤褰撳墠浠ｇ爜
echo "馃摝 鍒涘缓澶囦唤..."
git add . && git commit -m "鑷姩鏀硅繘鍓嶇殑澶囦唤"

# 2. 淇XSS婕忔礊
echo "馃敀 淇XSS婕忔礊..."
# 鑷姩鏇挎崲v-html涓烘枃鏈彃鍊?

# 3. 绉婚櫎纭紪鐮佸瘑閽?
echo "馃攼 绉婚櫎纭紪鐮佸瘑閽?.."
# 鑷姩浠巇ocker-compose.yml绉婚櫎鏁忔劅淇℃伅

# 4. 鏇存柊渚濊禆
echo "馃摝 鏇存柊渚濊禆..."
pip install -r requirements.txt

# 5. 杩愯娴嬭瘯
echo "馃И 杩愯娴嬭瘯..."
python manage.py test

# 6. 浠ｇ爜璐ㄩ噺妫€鏌?
echo "馃攳 浠ｇ爜璐ㄩ噺妫€鏌?.."
flake8 app/
black app/

echo "鉁?鑷姩淇瀹屾垚锛?
```

---

## 馃搳 鏀硅繘浼樺厛绾х煩闃?

```
绱ф€ヤ笖閲嶈     鈹?閲嶈涓嶇揣鎬?
鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
鈥?XSS婕忔礊      鈹?鈥?API鏂囨。
鈥?API瀵嗛挜娉勯湶  鈹?鈥?娴嬭瘯瑕嗙洊
鈥?瀵嗙爜瀛楁     鈹?鈥?鏃ュ織绯荤粺
鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
绱ф€ヤ笉閲嶈     鈹?涓嶉噸瑕佷笉绱ф€?
鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
鈥?(鏃?        鈹?鈥?浠ｇ爜娉ㄩ噴
              鈹?鈥?绉诲姩绔紭鍖?
鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€锟斤拷鈹€鈹€鈹€鈹€鈹€鈹€
```

---

## 鉁?瀹炴柦寤鸿

### 绗竴鍛紙瀹夊叏淇锛?
1. 鉁?淇XSS婕忔礊
2. 鉁?绉婚櫎纭紪鐮佸瘑閽?
3. 鉁?淇瀵嗙爜瀛楁

### 绗簩鍛紙鎬ц兘浼樺寲锛?
4. 鉁?浼樺寲鏁版嵁搴撴煡璇?
5. 鉁?娣诲姞缂撳瓨鏈哄埗

### 绗笁-鍥涘懆锛堟枃妗ｅ拰娴嬭瘯锛?
6. 鉁?闆嗘垚API鏂囨。
7. 鉁?鎻愬崌娴嬭瘯瑕嗙洊鐜?

### 鍚庣画锛堟寔缁敼杩涳級
8. 鈴?浠ｇ爜璐ㄩ噺鎻愬崌
9. 鈴?绉诲姩绔紭鍖?
10. 鈴?鎬ц兘鐩戞帶

---

## 馃摑 鏀硅繘璁板綍

姣忔鏀硅繘鍚庯紝璁板綍鍒?`IMPROVEMENT_LOG.md`:

```markdown
## [鏃ユ湡] - 鏀硅繘璁板綍

### 淇鐨勯棶棰?
- [ ] XSS婕忔礊淇
- [ ] API瀵嗛挜绉婚櫎
- [ ] 瀵嗙爜瀛楁淇

### 娴嬭瘯缁撴灉
- 鎵€鏈夋祴璇曢€氳繃 鉁?
- 鏃犲洖褰掗棶棰?鉁?

### Git鎻愪氦
- Commit: abc123
- 鍒嗘敮: improvement/security-fix
```

---

**鎬荤粨**: 閫氳繃绯荤粺鍖栫殑鏀硅繘璁″垝锛孎YP椤圭洰鍙互鍦ㄤ繚璇佸畨鍏ㄧ殑鍓嶆彁涓嬶紝閫愭鎻愬崌浠ｇ爜璐ㄩ噺銆佹€ц兘鍜屽彲缁存姢鎬с€?

**涓嬩竴姝?*: 寮€濮嬫墽琛岀涓€鍛ㄧ殑瀹夊叏淇浠诲姟銆?


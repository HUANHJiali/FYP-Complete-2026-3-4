"""
验证码生成工具
生成图形验证码用于登录安全
"""

import random
import string
import io
import base64
from django.core.cache import cache


class CaptchaUtil:
    """验证码工具类"""
    
    CACHE_PREFIX = 'captcha_'
    EXPIRE_TIME = 300  # 5分钟过期
    
    @staticmethod
    def generate_code(length=4):
        """生成随机验证码字符串"""
        chars = string.ascii_uppercase + string.digits
        # 排除容易混淆的字符
        chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
        return ''.join(random.choices(chars, k=length))
    
    @staticmethod
    def generate_image_base64(code):
        """生成验证码图片的base64编码"""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            # 如果没有PIL，返回简单的SVG
            return CaptchaUtil._generate_svg_base64(code)
        
        width, height = 120, 40
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 使用默认字体
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
        except:
            font = ImageFont.load_default()
        
        # 绘制验证码文字
        text_width = len(code) * 25
        x = (width - text_width) // 2
        for i, char in enumerate(code):
            # 随机颜色
            color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
            # 随机偏移
            y = random.randint(5, 15)
            draw.text((x + i * 25, y), char, font=font, fill=color)
        
        # 添加干扰线
        for _ in range(3):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill=(200, 200, 200), width=1)
        
        # 添加噪点
        for _ in range(100):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            draw.point((x, y), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        
        # 转换为base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f'data:image/png;base64,{img_base64}'
    
    @staticmethod
    def _generate_svg_base64(code):
        """生成SVG格式的验证码（不需要PIL）"""
        svg_template = '''
        <svg xmlns="http://www.w3.org/2000/svg" width="120" height="40">
            <rect width="100%" height="100%" fill="#f0f0f0"/>
            <text x="50%" y="50%" font-family="Arial" font-size="24" 
                  text-anchor="middle" dominant-baseline="middle" fill="#333">
                {code}
            </text>
        </svg>
        '''
        svg_content = svg_template.format(code=code)
        svg_base64 = base64.b64encode(svg_content.encode()).decode()
        return f'data:image/svg+xml;base64,{svg_base64}'
    
    @staticmethod
    def create_captcha():
        """创建验证码并返回验证码ID和图片"""
        code = CaptchaUtil.generate_code()
        captcha_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        
        # 存储验证码到缓存
        cache_key = f'{CaptchaUtil.CACHE_PREFIX}{captcha_id}'
        cache.set(cache_key, code.upper(), CaptchaUtil.EXPIRE_TIME)
        
        # 生成图片
        image_base64 = CaptchaUtil.generate_image_base64(code)
        
        return {
            'captchaId': captcha_id,
            'captchaImage': image_base64
        }
    
    @staticmethod
    def verify_captcha(captcha_id, user_input):
        """验证验证码"""
        if not captcha_id or not user_input:
            return False
        
        cache_key = f'{CaptchaUtil.CACHE_PREFIX}{captcha_id}'
        stored_code = cache.get(cache_key)
        
        # 验证后删除验证码（一次性使用）
        cache.delete(cache_key)
        
        if not stored_code:
            return False
        
        return stored_code.upper() == user_input.upper()


class LoginSecurity:
    """登录安全工具类"""
    
    LOCK_PREFIX = 'login_lock_'
    ATTEMPT_PREFIX = 'login_attempt_'
    MAX_ATTEMPTS = 5
    LOCK_TIME = 1800  # 30分钟
    
    @staticmethod
    def check_locked(username):
        """检查账号是否被锁定"""
        cache_key = f'{LoginSecurity.LOCK_PREFIX}{username}'
        locked_until = cache.get(cache_key)
        if locked_until:
            import time
            remaining = int(locked_until - time.time())
            if remaining > 0:
                return True, remaining
            else:
                cache.delete(cache_key)
        return False, 0
    
    @staticmethod
    def record_failed_attempt(username):
        """记录登录失败次数"""
        attempt_key = f'{LoginSecurity.ATTEMPT_PREFIX}{username}'
        attempts = cache.get(attempt_key, 0) + 1
        cache.set(attempt_key, attempts, LoginSecurity.LOCK_TIME)
        
        if attempts >= LoginSecurity.MAX_ATTEMPTS:
            # 锁定账号
            import time
            lock_key = f'{LoginSecurity.LOCK_PREFIX}{username}'
            cache.set(lock_key, time.time() + LoginSecurity.LOCK_TIME, LoginSecurity.LOCK_TIME)
            return True, LoginSecurity.LOCK_TIME
        
        remaining = LoginSecurity.MAX_ATTEMPTS - attempts
        return False, remaining
    
    @staticmethod
    def clear_failed_attempts(username):
        """清除登录失败记录"""
        attempt_key = f'{LoginSecurity.ATTEMPT_PREFIX}{username}'
        cache.delete(attempt_key)
    
    @staticmethod
    def get_remaining_attempts(username):
        """获取剩余尝试次数"""
        attempt_key = f'{LoginSecurity.ATTEMPT_PREFIX}{username}'
        attempts = cache.get(attempt_key, 0)
        return max(0, LoginSecurity.MAX_ATTEMPTS - attempts)

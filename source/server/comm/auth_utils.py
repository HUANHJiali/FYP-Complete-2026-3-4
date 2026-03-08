"""
JWT认证工具模块

提供JWT token的生成、验证和刷新功能。
替换原有的简单UUID token机制，提供更高的安全性和更好的用户体验。

主要功能：
1. 生成JWT token（包含用户信息和过期时间）
2. 验证JWT token
3. 刷新JWT token
4. 从token中提取用户信息

"""

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class JWTUtils:
    """JWT工具类"""

    # Token过期时间配置（小时）
    ACCESS_TOKEN_EXPIRE_HOURS = 24
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    # Token类型
    TOKEN_TYPE_ACCESS = 'access'
    TOKEN_TYPE_REFRESH = 'refresh'

    @staticmethod
    def _get_secret_key():
        """获取JWT密钥"""
        # 优先使用专门的JWT密钥，否则使用Django SECRET_KEY
        return getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)

    @staticmethod
    def _get_algorithm():
        """获取JWT算法"""
        return getattr(settings, 'JWT_ALGORITHM', 'HS256')

    @staticmethod
    def generate_tokens(user_id, user_type=None, additional_claims=None):
        """
        生成访问token和刷新token

        Args:
            user_id: 用户ID
            user_type: 用户类型（可选）
            additional_claims: 额外的声明信息（可选）

        Returns:
            dict: {
                'access_token': str,
                'refresh_token': str,
                'expires_in': int,  # 秒数
                'token_type': 'Bearer'
            }
        """
        now = datetime.utcnow()
        access_expire = now + timedelta(hours=JWTUtils.ACCESS_TOKEN_EXPIRE_HOURS)
        refresh_expire = now + timedelta(days=JWTUtils.REFRESH_TOKEN_EXPIRE_DAYS)

        # 基础payload
        base_payload = {
            'user_id': user_id,
            'iat': now,
            'iss': 'fyp-exam-system',  # 签发者
        }

        # 添加用户类型
        if user_type is not None:
            base_payload['user_type'] = user_type

        # 添加额外声明
        if additional_claims:
            base_payload.update(additional_claims)

        # 生成访问token
        access_payload = base_payload.copy()
        access_payload.update({
            'exp': access_expire,
            'type': JWTUtils.TOKEN_TYPE_ACCESS,
        })

        # 生成刷新token
        refresh_payload = base_payload.copy()
        refresh_payload.update({
            'exp': refresh_expire,
            'type': JWTUtils.TOKEN_TYPE_REFRESH,
        })

        secret_key = JWTUtils._get_secret_key()
        algorithm = JWTUtils._get_algorithm()

        try:
            access_token = jwt.encode(access_payload, secret_key, algorithm=algorithm)
            refresh_token = jwt.encode(refresh_payload, secret_key, algorithm=algorithm)

            # 缓存刷新token（用于验证和黑名单）
            cache_key = f'refresh_token:{user_id}'
            cache.set(cache_key, refresh_token, JWTUtils.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)

            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': JWTUtils.ACCESS_TOKEN_EXPIRE_HOURS * 3600,
                'token_type': 'Bearer'
            }
        except Exception as e:
            logger.error(f"生成JWT token失败: {str(e)}")
            raise

    @staticmethod
    def verify_token(token, token_type=TOKEN_TYPE_ACCESS):
        """
        验证JWT token

        Args:
            token: JWT token字符串
            token_type: token类型（access或refresh）

        Returns:
            dict: 解码后的payload，验证失败返回None
        """
        if not token:
            logger.warning("Token为空")
            return None

        secret_key = JWTUtils._get_secret_key()
        algorithm = JWTUtils._get_algorithm()

        try:
            # 解码token
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])

            # 验证token类型
            if payload.get('type') != token_type:
                logger.warning(f"Token类型不匹配，期望: {token_type}, 实际: {payload.get('type')}")
                return None

            # 验证签发者
            if payload.get('iss') != 'fyp-exam-system':
                logger.warning(f"Token签发者不匹配: {payload.get('iss')}")
                return None

            # 如果是刷新token，验证是否在缓存中
            if token_type == JWTUtils.TOKEN_TYPE_REFRESH:
                user_id = payload.get('user_id')
                cache_key = f'refresh_token:{user_id}'
                cached_token = cache.get(cache_key)
                if cached_token != token:
                    logger.warning(f"刷新token不在缓存中或已失效: user_id={user_id}")
                    return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效的token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"验证token时发生错误: {str(e)}")
            return None

    @staticmethod
    def refresh_tokens(refresh_token):
        """
        使用刷新token获取新的访问token

        Args:
            refresh_token: 刷新token字符串

        Returns:
            dict: 新的token对，失败返回None
        """
        # 验证刷新token
        payload = JWTUtils.verify_token(refresh_token, JWTUtils.TOKEN_TYPE_REFRESH)
        if not payload:
            logger.warning("刷新token验证失败")
            return None

        user_id = payload.get('user_id')
        user_type = payload.get('user_type')

        # 生成新的token对
        try:
            new_tokens = JWTUtils.generate_tokens(user_id, user_type)

            # 使旧的刷新token失效
            cache_key = f'refresh_token:{user_id}'
            cache.delete(cache_key)

            return new_tokens
        except Exception as e:
            logger.error(f"刷新token失败: {str(e)}")
            return None

    @staticmethod
    def revoke_token(token):
        """
        撤销token（将其加入黑名单）

        Args:
            token: 要撤销的token字符串

        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            payload = jwt.decode(
                token,
                JWTUtils._get_secret_key(),
                algorithms=[JWTUtils._get_algorithm()],
                options={"verify_exp": False}  # 不验证过期时间
            )

            user_id = payload.get('user_id')
            exp = payload.get('exp')

            # 如果token已过期，不需要撤销
            if exp and exp < datetime.utcnow().timestamp():
                return True

            # 将token加入黑名单（缓存到过期时间）
            if exp:
                cache_key = f'blacklist_token:{token}'
                ttl = int(exp - datetime.utcnow().timestamp())
                if ttl > 0:
                    cache.set(cache_key, True, ttl)

            # 删除刷新token缓存
            cache_key = f'refresh_token:{user_id}'
            cache.delete(cache_key)

            return True
        except Exception as e:
            logger.error(f"撤销token失败: {str(e)}")
            return False

    @staticmethod
    def is_token_blacklisted(token):
        """
        检查token是否在黑名单中

        Args:
            token: JWT token字符串

        Returns:
            bool: 在黑名单中返回True
        """
        cache_key = f'blacklist_token:{token}'
        return cache.get(cache_key) is not None

    @staticmethod
    def get_user_id_from_token(token):
        """
        从token中提取用户ID（便捷方法）

        Args:
            token: JWT token字符串

        Returns:
            str: 用户ID，失败返回None
        """
        payload = JWTUtils.verify_token(token)
        return payload.get('user_id') if payload else None


# 向后兼容的函数（用于替换原有的UUID token逻辑）
def generate_token(user_id, user_type=None):
    """生成token（向后兼容接口）"""
    tokens = JWTUtils.generate_tokens(user_id, user_type)
    return tokens['access_token']


def verify_token(token):
    """验证token（向后兼容接口）"""
    return JWTUtils.get_user_id_from_token(token)


def revoke_token(token):
    """撤销token（向后兼容接口）"""
    return JWTUtils.revoke_token(token)

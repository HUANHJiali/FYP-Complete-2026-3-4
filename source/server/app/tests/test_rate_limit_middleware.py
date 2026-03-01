from django.test import SimpleTestCase
from types import SimpleNamespace
from unittest.mock import patch

from app.middleware import RateLimitMiddleware


class RateLimitMiddlewareTest(SimpleTestCase):
    def setUp(self):
        self.middleware = RateLimitMiddleware(lambda request: None)

    def test_exact_path_limit(self):
        self.assertEqual(self.middleware.get_rate_limit('/api/login/'), 10)

    def test_admin_prefix_limit(self):
        self.assertEqual(self.middleware.get_rate_limit('/api/admin/users/'), 100)

    def test_default_limit(self):
        self.assertEqual(self.middleware.get_rate_limit('/api/unknown/path/'), 60)

    def test_client_ip_from_x_forwarded_for(self):
        request = SimpleNamespace(META={
            'HTTP_X_FORWARDED_FOR': '1.1.1.1, 2.2.2.2',
            'REMOTE_ADDR': '4.4.4.4',
        })
        with patch.object(self.middleware, 'trust_proxy_headers', True):
            self.assertEqual(self.middleware.get_client_ip(request), '1.1.1.1')

    def test_client_ip_from_x_real_ip(self):
        request = SimpleNamespace(META={
            'HTTP_X_REAL_IP': '3.3.3.3',
            'REMOTE_ADDR': '4.4.4.4',
        })
        with patch.object(self.middleware, 'trust_proxy_headers', True):
            self.assertEqual(self.middleware.get_client_ip(request), '3.3.3.3')

    def test_ignore_proxy_headers_by_default(self):
        request = SimpleNamespace(META={
            'HTTP_X_FORWARDED_FOR': '1.1.1.1',
            'HTTP_X_REAL_IP': '3.3.3.3',
            'REMOTE_ADDR': '4.4.4.4',
        })
        self.assertEqual(self.middleware.get_client_ip(request), '4.4.4.4')

    def test_client_ip_from_remote_addr(self):
        request = SimpleNamespace(META={'REMOTE_ADDR': '4.4.4.4'})
        self.assertEqual(self.middleware.get_client_ip(request), '4.4.4.4')

    def test_client_ip_unknown_fallback(self):
        request = SimpleNamespace(META={})
        self.assertEqual(self.middleware.get_client_ip(request), 'unknown')

from django.conf import settings


class ApiCsrfExemptMiddleware:
    """
    仅对白名单路径豁免 CSRF，避免 BaseView 全量豁免。
    默认豁免 /api/ 路径（可通过 CSRF_EXEMPT_PATH_PREFIXES 配置）。
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_prefixes = tuple(getattr(settings, 'CSRF_EXEMPT_PATH_PREFIXES', ['/api/']))

    def __call__(self, request):
        path = request.path or ''
        if self.exempt_prefixes and path.startswith(self.exempt_prefixes):
            request._dont_enforce_csrf_checks = True
        return self.get_response(request)

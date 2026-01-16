# apps/core/middleware/audit.py
from django.utils.deprecation import MiddlewareMixin

class AuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Пока пусто — логика аудита будет позже
        pass
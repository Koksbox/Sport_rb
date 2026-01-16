# apps/core/middleware/consent.py
from django.utils.deprecation import MiddlewareMixin

class ConsentMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Пока пусто — можно расширить для ФЗ-152
        pass
from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class AllowUserWithSecretKey(MiddlewareMixin):

    def process_request(self, request):
        if request.path.startswith('/api/'):
            if request.headers.get('Authorization') != settings.SECRET_KEY:
                return HttpResponse('Unauthorized', status=401)
        return None
        
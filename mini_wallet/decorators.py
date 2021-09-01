from django.http import JsonResponse
from django.utils import timezone
from functools import wraps
from mini_wallet.authentication.models import UserLogging

def authenticate_user(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        if 'HTTP_AUTHORIZATION' in request.META:
            header_auth = request.META['HTTP_AUTHORIZATION']
            token = header_auth.split(' ', 1)

            if token[0] == 'Token':
                token = UserLogging.objects.filter(token=token[1]).first()
                if token and token.expired > timezone.now():
                    request.user = token.user
                    return function(request, *args, **kwargs)

            return JsonResponse({
                "status": "error",
                "message": "Unauthorized"
            }, status=401)

        else:
            return JsonResponse({
                "status": "error",
                "message": "Unauthorized"
            }, status=401)

    return decorator
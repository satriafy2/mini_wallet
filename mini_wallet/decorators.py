from django.http import JsonResponse
from functools import wraps

def authenticate_user(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        if 'HTTP_AUTHORIZATION' in request.META:
           auth = request.META['HTTP_AUTHORIZATION']
           print(auth)
           return function(request, *args, **kwargs)

        else:
            return JsonResponse({
                "status": "error",
                "message": "Unauthorized"
            }, status=401)

    return decorator
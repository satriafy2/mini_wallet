from django.http import JsonResponse


def init_wallet(request):
    return JsonResponse({
        "data": {
            "token": "adsfij908sdjfoi"
        },
        "status": "success"
    }, status=200)

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from mini_wallet.decorators import authenticate_user


@method_decorator(authenticate_user, name='dispatch')
class WalletView(View):
    def post(self, request):
        pass

    def get(self, request):
        return JsonResponse({
            "data": {
                "token": "adsfij908sdjfoi"
            },
            "status": "success"
        }, status=200)

    def patch(self, request):
        pass
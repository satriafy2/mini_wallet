from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from mini_wallet.decorators import authenticate_user
from mini_wallet.wallet.models import ActivationHistory, Wallet


@method_decorator(authenticate_user, name='dispatch')
class WalletView(View):
    def post(self, request):
        pass

    def get(self, request):
        wallet = Wallet.objects.get(user=request.user)
        if not wallet.status:
            return JsonResponse({
                "status": "fail",
                "data": {
                    "error": "Disabled"
                }
            }, status=400)

        last_action = wallet.activation_history.filter(
            action=ActivationHistory.WALLET_ENABLE).last()
        return JsonResponse({
            "status": "success",
            "data": {
                "wallet": {
                    "id": wallet.id,
                    "owned_by": wallet.user.user_uuid,
                    "status": "enabled",
                    "enabled_at": last_action.created_at,
                    "balance": wallet.balance
                }
            }
        }, status=200)

    def patch(self, request):
        pass
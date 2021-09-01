import json

from django.http import JsonResponse
from django.http.request import QueryDict
from django.utils.decorators import method_decorator
from django.views import View
from django.http.multipartparser import MultiPartParser

from mini_wallet.decorators import authenticate_user
from mini_wallet.wallet.models import ActivationHistory, Wallet


@method_decorator(authenticate_user, name='dispatch')
class WalletView(View):
    def dispatch(self, request, *args, **kwargs):
        self.wallet = Wallet.objects.get(user=request.user)
        return super(WalletView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        if self.wallet.status:
            return JsonResponse({
                "status": "fail",
                "data": {
                    "error": "Already enabled"
                }
            }, status=400)
        
        self.wallet.status = True
        self.wallet.save(update_fields=['status'])
        activation = ActivationHistory(wallet=self.wallet, action=ActivationHistory.WALLET_ENABLE)
        activation.save()

        return JsonResponse({
            "status": "success",
            "data": {
                "wallet": {
                    "id": self.wallet.id,
                    "owned_by": request.user.user_uuid,
                    "status": "enabled",
                    "enabled_at": activation.created_at,
                    "balance": float(self.wallet.balance)
                }
            }
        }, status=200)

    def get(self, request):
        if not self.wallet.status:
            return JsonResponse({
                "status": "fail",
                "data": {
                    "error": "Disabled"
                }
            }, status=400)

        last_action = self.wallet.activation_history.filter(
            action=ActivationHistory.WALLET_ENABLE).last()
        return JsonResponse({
            "status": "success",
            "data": {
                "wallet": {
                    "id": self.wallet.id,
                    "owned_by": self.wallet.user.user_uuid,
                    "status": "enabled",
                    "enabled_at": last_action.created_at,
                    "balance": float(self.wallet.balance)
                }
            }
        }, status=200)

    def patch(self, request):
        data = MultiPartParser(request.META, request, request.upload_handlers).parse()
        if not data[0]['is_disabled'] or data[0]['is_disabled'] != 'true':
            return JsonResponse({
                "status": "fail",
                "data": {
                    "error": {
                        "is_disabled": "Missing or invalid data."
                    }
                }
            }, status=400)
        
        self.wallet.status = False
        self.wallet.save(update_fields=['status'])
        activation = ActivationHistory(wallet=self.wallet, action=ActivationHistory.WALLET_DISABLE)
        activation.save()
        
        return JsonResponse({
            "status": "success",
            "data": {
                "wallet": {
                    "id": self.wallet.id,
                    "owned_by": request.user.user_uuid,
                    "status": "disabled",
                    "disabled_at": activation.created_at,
                    "balance": float(self.wallet.balance)
                }
            }
        })

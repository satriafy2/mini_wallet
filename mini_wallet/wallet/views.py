from django.http import JsonResponse
from django.http.multipartparser import MultiPartParser
from django.http.response import HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST

from mini_wallet.decorators import authenticate_user
from mini_wallet.utils import is_valid_uuid
from mini_wallet.wallet.models import ActivationHistory, UsageHistory, Wallet


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


@require_POST
@authenticate_user
def use_wallet(request, action):
    wallet = Wallet.objects.get(user=request.user)
    if not wallet.status:
        return JsonResponse({
            "status": "fail",
            "data": {
                "error": "Disabled"
            }
        })
    
    amount = request.POST.get('amount', None)
    reference_id = request.POST.get('reference_id', None)
    if None in [amount, reference_id]:
        return JsonResponse({
            "status": "fail",
            "data": {
                "error": "Missing required fields. (amount, reference_id)"
            }
        }, status=400)

    if is_valid_uuid(reference_id):
        wallet_usage = UsageHistory.objects.filter(reference_id=reference_id)
        if wallet_usage:
            return JsonResponse({
                "status": "fail",
                "data": {
                    "error": {
                        "reference_id": "reference_id exist."
                    }
                }
            }, status=400)    
    
    else: 
        return JsonResponse({
            "status": "fail",
            "data": {
                "error": {
                    "reference_id": "Invalid reference_id format."
                }
            }
        }, status=400)

    amount = float(amount)
    if action == 'deposits':
        wallet.balance = float(wallet.balance) + amount
        wallet.save(update_fields=['balance'])
        wallet_usage = UsageHistory(
            wallet=wallet,
            amount=amount,
            reference_id=reference_id,
            action=UsageHistory.DEPOSIT
        )
        wallet_usage.save()

        return JsonResponse({
            "status": "success",
            "data": {
                "deposit": {
                    "id": wallet.id,
                    "deposited_by": request.user.user_uuid,
                    "status": "success",
                    "deposited_at": wallet_usage.created_at,
                    "amount": amount,
                    "reference_id": reference_id
                }
            }
        })

    elif action == 'withdrawals':
        if wallet.balance < amount:
            return JsonResponse({
                "status": "fail",
                "data": {
                    "error": "Withdrawal amount is more than current balance."
                }
            })
        
        wallet.balance = float(wallet.balance) - amount
        wallet.save(update_fields=['balance'])
        wallet_usage = UsageHistory(
            wallet=wallet,
            amount=amount,
            reference_id=reference_id,
            action=UsageHistory.WITHDRAWAL
        )
        wallet_usage.save()

        return JsonResponse({
            "status": "success",
            "data": {
                "withdrawal": {
                    "id": wallet.id,
                    "withdrawn_by": request.user.user_uuid,
                    "status": "success",
                    "withdrawn_at": wallet_usage.created_at,
                    "amount": amount,
                    "reference_id": reference_id
                }
            }
        })

    else:
        return HttpResponseNotFound()

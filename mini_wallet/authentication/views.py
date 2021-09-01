from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from mini_wallet.authentication.models import User
from mini_wallet.utils import generate_token
from mini_wallet.wallet.models import Wallet


def init_wallet(request):
    cust_id = request.POST.get('customer_xid', None)
    if not cust_id:
        return JsonResponse({
            "data": {
                "error": {
                    "customer_xid": [
                        "Missing data for required field."
                    ]
                }
            },
            "status": "fail"
        }, status=400)

    customer = get_object_or_404(User, user_uuid=cust_id)
    wallet = Wallet.objects.filter(user=customer).first()

    if not wallet:
        wallet = Wallet(user=customer).save()

    return JsonResponse({
        "data": {
            "token": generate_token(customer)
        },
        "status": "success"
    }, status=200)


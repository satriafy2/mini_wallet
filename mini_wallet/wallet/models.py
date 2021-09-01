import uuid

from django.db import models


class Wallet(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.OneToOneField(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name}'s Wallet"


class ActivationHistory(models.Model):
    WALLET_ENABLE = 'enable'
    WALLET_DISABLE = 'disable'
    ACTION_CHOICES = [
        (WALLET_ENABLE, 'Enabled'),
        (WALLET_DISABLE, 'Disabled'),
    ]

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='activation_history'
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)


class UsageHistory(models.Model):
    WITHDRAWAL = 'withdrawal'
    DEPOSIT = 'deposit'
    ACTION_CHOICES = [
        (WITHDRAWAL, 'Withdrawal'),
        (DEPOSIT, 'Deposit'),
    ]

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='usage_history'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

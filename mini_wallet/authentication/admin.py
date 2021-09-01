from django.contrib import admin
from mini_wallet.authentication.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

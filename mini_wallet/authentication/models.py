import uuid

from django.contrib.auth.models import User, AbstractUser
from django.db import models


class User(AbstractUser):
    user_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class UserLogging(models.Model):
    user = models.ForeignKey(User, related_name='logs', on_delete=models.CASCADE)
    token = models.CharField(max_length=128)
    created = models.DateTimeField(auto_now_add=True)
    expired = models.DateTimeField(null=True)

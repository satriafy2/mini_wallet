import hashlib
import uuid

from datetime import datetime, timedelta
from mini_wallet.authentication.models import UserLogging


def generate_token(user):
    expired = datetime.now() + timedelta(hours=2)
    token = f"{user.id}::{expired.isoformat()}"
    token = hashlib.sha256(token.encode('utf-8')).hexdigest()
    UserLogging(user=user, token=token, expired=expired).save()
    return token

def is_valid_uuid(data):
    try:
        uuid.UUID(str(data))
        return True
    except ValueError:
        return False

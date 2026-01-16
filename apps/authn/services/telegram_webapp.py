# apps/authn/services/telegram_webapp.py
import hashlib
import hmac
from urllib.parse import unquote


def validate_telegram_init_data(init_data: str, bot_token: str) -> dict:
    """Проверяет подлинность initData от Telegram WebApp"""
    try:
        pairs = [pair.split('=', 1) for pair in init_data.split('&')]
        data = {key: unquote(value) for key, value in pairs}

        hash_ = data.pop('hash')
        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()))

        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if computed_hash != hash_:
            raise ValueError("Invalid hash")
        return data
    except Exception:
        raise ValueError("Invalid initData")
import hashlib
import hmac

class CryptoService:
    @classmethod
    def sha256hash(cls, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    @classmethod
    def sha256hmac(cls, text: str, secret: str) -> str:
        return hmac.new(secret.encode(), text.encode(), hashlib.sha256).hexdigest()
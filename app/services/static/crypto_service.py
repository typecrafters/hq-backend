import hashlib
import hmac
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.config.settings import settings

class CryptoService:
    key = settings.encryption_key

    @classmethod
    def sha256hash(cls, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    @classmethod
    def sha256hmac(cls, text: str, secret: str) -> str:
        return hmac.new(secret.encode(), text.encode(), hashlib.sha256).hexdigest()
    
    @classmethod
    def aes_encrypt(cls, text: str) -> bytes:
        aesgcm = AESGCM(cls.key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, text.encode(), associated_data=None)
        return nonce + ciphertext

    @classmethod
    def aes_decrypt(cls, token: bytes) -> str:
        aesgcm = AESGCM(cls.key)
        nonce, ciphertext = token[:12], token[12:]
        plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
        return plaintext.decode()
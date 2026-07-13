from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash

class PasswordService:
    ph = PasswordHasher(
        time_cost=3,
        memory_cost=2**18,
        parallelism=4,
        hash_len=32,
        salt_len=16
    )

    @classmethod
    def hash(cls, password: str) -> str:
        return cls.ph.hash(password)
    
    @classmethod
    def compare(cls, hash: str, password: str) -> bool:
        try:
            cls.ph.verify(hash, password)
            return True
        except (VerifyMismatchError, InvalidHash):
            return False
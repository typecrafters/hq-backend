from datetime import timedelta
from typing import Self


class Duration:
    @classmethod
    def readable(cls, duration: timedelta, use_seconds: bool = False) -> str:
        words = []
        years = duration.days // 365
        if years:
            words.append(f"{years} {"year" if years == 1 else "years"}")
        months = (duration.days % 365) // 30
        if months:
            words.append(f"{months} {"month" if months == 1 else "months"}")
        days = ((duration.days % 365) % 30) 
        if days:
            words.append(f"{days} {"day" if days == 1 else "days"}")
        
        hours = duration.seconds // 3600
        if hours:
            words.append(f"{hours} {"hour" if hours == 1 else "hours"}")

        minutes = (duration.seconds % 3600) // 60

        if minutes:
            words.append(f"{minutes} {"minute" if minutes == 1 else "minutes"}")

        if use_seconds:
            seconds = ((duration.seconds % 3600) % 60) 
            if seconds:
                words.append(f"{seconds} {"second" if seconds == 1 else "seconds"}")



        return f"{', '.join(words[:-1])}{' and ' if len(words) > 1 else ''}{words[-1]}" if len(words) else ''
        

class Storage:
    __size: int

    __kb = pow(10, 3)
    __kib = pow(2, 10)
    __mb = pow(10, 6)
    __mib = pow(2, 20)
    __gb = pow(10, 9)
    __gib = pow(2, 30)
    __tb = pow(10, 12)
    __tib = pow(2, 40)

    def __init__(self, size: int) -> Self:
        self.__size = size

    @classmethod
    def of(cls, b: int) -> Self:
        return cls(b)

    @classmethod
    def of_kb(cls, kb: int) -> Self:
        return cls(kb * cls.__kb)

    @classmethod
    def of_kib(cls, kib: int) -> Self:
        return cls(kib * cls.__kib)

    @classmethod
    def of_mb(cls, mb: int) -> Self:
        return cls(mb * cls.__mb)

    @classmethod
    def of_mib(cls, mib: int) -> Self:
        return cls(mib * cls.__mib)

    @classmethod
    def of_gb(cls, gb: int) -> Self:
        return cls(gb * cls.__gb)

    @classmethod
    def of_gib(cls, gib: int) -> Self:
        return cls(gib * cls.__gib)

    @classmethod
    def of_tb(cls, tb: int) -> Self:
        return cls(tb * cls.__tb)

    @classmethod
    def of_tib(cls, tib: int) -> Self:
        return cls(tib * cls.__tib)
    
    def to_b(self) -> int:
        return self.__size
    
    def to_kb(self) -> int:
        return self.__size / self.__kb
    
    def to_kib(self) -> int:
        return self.__size / self.__kib
    
    def to_mb(self) -> int:
        return self.__size / self.__mb
    
    def to_mib(self) -> int:
        return self.__size / self.__mib
    
    def to_gb(self) -> int:
        return self.__size / self.__gb
    
    def to_gib(self) -> int:
        return self.__size / self.__gib
    
    def to_tb(self) -> int:
        return self.__size / self.__tb

    def to_tib(self) -> int:
        return self.__size / self.__tib
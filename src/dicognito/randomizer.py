import hashlib
import os


class Randomizer:
    def __init__(self, salt):
        if salt is None:
            salt = os.urandom(20)
        self.salt = str(salt)

    def to_int(self, original_value):
        message = self.salt + str(original_value)
        if isinstance(message, bytes):
            encoded = message
            hash = [ord(d) for d in hashlib.md5(encoded).digest()]
        else:
            encoded = message.encode("utf8")
            hash = hashlib.md5(encoded).digest()
        result = 0
        for c in hash:
            result *= 0x100
            result += c
        return result

    def get_ints_from_ranges(self, original_value, *suprenums):
        big_int = self.to_int(original_value)
        result = []
        for s in suprenums:
            result.append(big_int % s)
            big_int //= s
        return result

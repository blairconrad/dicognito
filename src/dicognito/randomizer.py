import datetime
import md5


class Randomizer:
    def __init__(self):
        self.salt = str(datetime.datetime.utcnow())

    def to_int(self, original_value):
        hash = md5.md5(self.salt + str(original_value)).digest()
        return reduce(lambda a, b: a * 0x100 + ord(b), hash, 0)

    def get_ints_from_ranges(self, original_value, *suprenums):
        big_int = self.to_int(original_value)
        result = []
        for s in suprenums:
            result.append(big_int % s)
            big_int /= s
        return result

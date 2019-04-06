import hashlib
import os


class Randomizer:
    def __init__(self, seed):
        """\
        Create a new Randomizer.

        Parameters
        ----------
        seed
            Not intended for general use. Seeds the data randomizer so it
            produces consistent results when anonymizing elements with the
            same initial values.
        """
        if seed is None:
            seed = os.urandom(20)
        self.seed = str(seed)

    def to_int(self, original_value):
        """\
        Convert an original data element value into a large integer,
        which can be used to select or construct a replacement value.

        Parameters
        ----------
        original_value
            The original value that will ultimately be replaced.
        """
        message = self.seed + str(original_value)
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
        """\
        Convert an original data element value into a series of
        integers, each between 0 (inclusive) and one of the suprenums
        (exclusive) passed in.

        Parameters
        ----------
        original_value
            The original value that will ultimately be replaced.

        suprenums : sequence of int
            The upper bounds for each of the desired integer ranges.
        """
        big_int = self.to_int(original_value)
        result = []
        for s in suprenums:
            result.append(big_int % s)
            big_int //= s
        return result

from __future__ import annotations

import hashlib
import os
from typing import Sequence


class Randomizer:
    def __init__(self, seed: str | None):
        """\
        Create a new Randomizer.

        Parameters
        ----------
        seed
            Used to convert input values into large integers.
            The results are completely determined by the
            given seed and the input value.
        """
        if seed is None:
            self.seed = str(os.urandom(20))
        else:
            self.seed = str(seed)

    def to_int(self, original_value: str) -> int:
        """\
        Convert an original data element value into a large integer,
        which can be used to select or construct a replacement value.

        Parameters
        ----------
        original_value
            The original value that will ultimately be replaced.
        """
        message = self.seed + original_value
        encoded = message.encode("utf8")
        digest = hashlib.md5(encoded).digest()  # noqa: S324
        result = 0
        for c in digest:
            result *= 0x100
            result += c
        return result

    def get_ints_from_ranges(self, original_value: str, *suprema: int) -> Sequence[int]:
        """\
        Convert an original data element value into a series of
        integers, each between 0 (inclusive) and one of the suprema
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
        for s in suprema:
            result.append(big_int % s)
            big_int //= s
        return result

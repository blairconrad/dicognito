import itertools
import operator
from typing import Callable, List, Sequence


class Summary:
    def __init__(self, *attributes: Sequence[str], key: Callable[[Sequence[str]], Sequence[str]] = lambda r: r):
        self.attributes = attributes
        self.rows: List[Sequence[str]] = []
        self.key = key

    def add_row(self, *row: str) -> None:
        self.rows.append(row)

    def print(self) -> None:
        print("%-16s %-16s %s" % self.attributes)
        print("%-16s %-16s %s" % tuple("-" * len(attribute) for attribute in self.attributes))

        sorted_rows = sorted(self.rows, key=self.key)  # type: ignore[arg-type]
        for row in map(operator.itemgetter(0), itertools.groupby(sorted_rows, key=self.key)):
            print("%-16s %-16s %s" % row)

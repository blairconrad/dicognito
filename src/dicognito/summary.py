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
        widths = [len(a) for a in self.attributes]

        sorted_rows = sorted(self.rows, key=self.key)  # type: ignore[arg-type]
        output_rows = list(map(operator.itemgetter(0), itertools.groupby(sorted_rows, key=self.key)))
        for row in output_rows:
            for (i, v) in enumerate(row):
                widths[i] = max(widths[i], len(v))

        format = " ".join("{" + str(i) + ":<" + str(width) + "}" for (i, width) in enumerate(widths))
        lines = tuple("-" * width for (i, width) in enumerate(widths))

        print(format.format(*self.attributes).rstrip())
        print(format.format(*lines))
        for row in output_rows:
            print(format.format(*row).rstrip())

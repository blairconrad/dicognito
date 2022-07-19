import itertools
import operator
from typing import List, Sequence


class Summarize:
    def __init__(self, *attributes: Sequence[str]):
        self.attributes = attributes
        self.rows: List[Sequence[str]] = []

    def add_row(self, *row: str) -> None:
        self.rows.append(row)

    def print(self) -> None:
        widths = [len(a) for a in self.attributes]

        sorted_rows = sorted(self.rows)  # type: ignore[type-var]
        output_rows = list(map(operator.itemgetter(0), itertools.groupby(sorted_rows)))
        for row in output_rows:
            for (i, v) in enumerate(row):
                widths[i] = max(widths[i], len(v))

        header_format = (
            "| " + " | ".join("{" + str(i) + ":^" + str(width) + "}" for (i, width) in enumerate(widths)) + " |"
        )
        row_format = header_format.replace("^", "<")
        lines = tuple("-" * width for (i, width) in enumerate(widths))

        print(header_format.format(*self.attributes))
        print(header_format.format(*lines))
        for row in output_rows:
            print(row_format.format(*row))

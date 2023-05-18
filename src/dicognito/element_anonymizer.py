from typing import Iterator
from pydicom import DataElement
from pydicom.dataset import Dataset


class ElementAnonymizer:
    def __call__(self, dataset: Dataset, data_element: DataElement) -> bool:
        raise NotImplementedError

    def describe_actions(self) -> Iterator[str]:
        raise NotImplementedError

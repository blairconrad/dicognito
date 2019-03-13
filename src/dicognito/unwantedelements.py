import pydicom


class UnwantedElementsStripper:
    def __init__(self, *tag_names):
        self.tags = [
            pydicom.datadict.tag_for_keyword(tag_name) for tag_name in tag_names
        ]

    def __call__(self, dataset, data_element):
        if data_element.tag in self.tags:
            del dataset[data_element.tag]
            return True
        return False

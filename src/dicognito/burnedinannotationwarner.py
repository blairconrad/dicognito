"""\
Defines BurnedAnnotationWarner, the class that generates warnings for the BurnedInAnnontation attribute.
"""


class BurnedInAnnotationWarner:
    def __init__(self, warn_level):
        """\
        Create a new BurnedInAnnotationWarner.

        Parameters
        ----------
        warn_level : str
            Desired level of warning. Can be one of "never",
            "if-yes", "unless-no", or unspecified.
            If value is unspecified or invalid, the warn_level
            of "if-yes" is used.
        """
        self.warn_level = warn_level

    def generate_warning(self, dataset):
        """\
        Potentially generate a warning based on the self.warn_level
        and the BurnedInAnnotation attribute value in dataset.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to examine.

        Returns
        -------
        The warning message.
        """
        if "BurnedInAnnotation" not in dataset:
            if self.warn_level == "unless-no":
                return "Burned In Annotation attribute value does not exist."
        elif (self.warn_level == "if-yes" and dataset.BurnedInAnnotation == "YES") or (
            self.warn_level == "unless-no" and dataset.BurnedInAnnotation != "NO"
        ):
            return "Burned In Annotation attribute value is {}.".format(dataset.BurnedInAnnotation)

        return ""

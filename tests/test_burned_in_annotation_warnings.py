import pytest

from dicognito.burnedinannotationwarner import BurnedInAnnotationWarner

from .data_for_tests import load_test_instance

file_name = "file.dcm"
message_file_prefix = f"File {file_name}: "


@pytest.mark.parametrize(
    "warn_level,attribute_value,expected_warning",
    [
        ("never", "YES", ""),
        ("never", "NO", ""),
        ("never", "InvalidValue", ""),
        ("if-yes", "YES", f"{message_file_prefix}Burned In Annotation attribute value is YES."),
        ("if-yes", "NO", ""),
        ("if-yes", "InvalidValue", ""),
        ("unless-no", "YES", f"{message_file_prefix}Burned In Annotation attribute value is YES."),
        ("unless-no", "NO", ""),
        ("unless-no", "InvalidValue", f"{message_file_prefix}Burned In Annotation attribute value is InvalidValue."),
    ],
)
def test_attribute_exists(warn_level, attribute_value, expected_warning):
    with load_test_instance() as dataset:
        dataset.BurnedInAnnotation = attribute_value

        burned_in_annotation_warner = BurnedInAnnotationWarner(warn_level)
        actual_warning = burned_in_annotation_warner.generate_warning(file_name, dataset)

        assert actual_warning == expected_warning


@pytest.mark.parametrize(
    "warn_level,expected_warning",
    [
        ("never", ""),
        ("if-yes", ""),
        ("unless-no", f"{message_file_prefix}Burned In Annotation attribute value does not exist."),
    ],
)
def test_attribute_does_not_exist(warn_level, expected_warning):
    with load_test_instance() as dataset:
        assert "BurnedInAnnotation" not in dataset

        burned_in_annotation_warner = BurnedInAnnotationWarner(warn_level)
        actual_warning = burned_in_annotation_warner.generate_warning(file_name, dataset)

        assert actual_warning == expected_warning

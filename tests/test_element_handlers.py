import pytest

from dicognito.exceptions import TagError
from dicognito.value_keeper import ValueKeeper


def test_value_keeper_raises_good_exception_on_bad_tag():
    with pytest.raises(TagError) as e:
        ValueKeeper("BADTAG")

    assert (
        str(e.value) == "Bad tag name 'BADTAG'. Must be a well-known DICOM element name or a string in the form "
        "'stuv,wxyz' where each character is a hexadecimal digit."
    )


@pytest.mark.parametrize(
    ("tag_name", "expected_tag_name"),
    [
        ("PatientName", "PatientName"),
        ("0010,0010", "PatientName"),
        ("BA10,01AB", "BA10,01AB"),
    ],
)
def test_value_keeper_describes_action(tag_name: str, expected_tag_name: str) -> None:
    description = "".join(ValueKeeper(tag_name).describe_actions())
    assert description == f"Keep {expected_tag_name} values"

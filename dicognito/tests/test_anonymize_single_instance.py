import os
import pydicom
import pytest
from pydicom.data import get_testdata_files

from dicognito.anonymizer import Anonymizer
from dicognito.pnanonymizer import PNAnonymizer

LAST = 0
FIRST = 1
MIDDLE = 2


def load_test_instance():
    dataset = load_dcm(get_testdata_files('MR_small.dcm')[0])
    source_image_dataset = pydicom.dataset.Dataset()
    source_image_dataset.ReferencedSOPClassUID = ['1.2.3.0.1']
    source_image_dataset.ReferencedSOPInstanceUID = ['1.2.3.1.1']
    dataset.SourceImageSequence = pydicom.sequence.Sequence(
        [source_image_dataset])
    return dataset


@pytest.mark.parametrize('element_path', [
    'file_meta.MediaStorageSOPClassUID',
    'file_meta.TransferSyntaxUID',
    'file_meta.ImplementationClassUID',
    'SOPClassUID',
    'SourceImageSequence[0].ReferencedSOPClassUID',
])
def test_nonidentifying_uis_are_left_alone(element_path):
    with load_test_instance() as dataset:

        expected = eval('dataset.' + element_path)

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = eval('dataset.' + element_path)

        assert actual == expected


@pytest.mark.parametrize('element_path', [
    'file_meta.MediaStorageSOPInstanceUID',
    'SOPInstanceUID',
    'SourceImageSequence[0].ReferencedSOPInstanceUID',
    'StudyInstanceUID',
    'SeriesInstanceUID',
    'FrameOfReferenceUID',
])
def test_identifying_uis_are_updated(element_path):
    with load_test_instance() as dataset:

        expected = eval('dataset.' + element_path)

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = eval('dataset.' + element_path)

        assert actual != expected


@pytest.mark.parametrize('one_element_path,another_element_path', [
    ('file_meta.MediaStorageSOPInstanceUID', 'SOPInstanceUID'),
])
def test_repeated_identifying_uis_get_same_values(one_element_path, another_element_path):
    with load_test_instance() as dataset:

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        one_uid = eval('dataset.' + one_element_path)
        another_uid = eval('dataset.' + another_element_path)

        assert one_uid == another_uid


def test_female_patient_name_gets_anonymized():
    with load_test_instance() as dataset:
        dataset.PatientSex = 'F'
        dataset.PatientName = 'LAST^FIRST^MIDDLE'

        original_patient_name = dataset.PatientName

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_patient_name = dataset.PatientName

        assert new_patient_name != original_patient_name
        assert (new_patient_name.split('^')[LAST]
                in PNAnonymizer._last_names)
        assert (new_patient_name.split('^')[FIRST]
                in PNAnonymizer._female_first_names)
        assert (new_patient_name.split('^')[MIDDLE]
                in PNAnonymizer._all_first_names)


def test_male_patient_name_gets_anonymized():
    with load_test_instance() as dataset:
        dataset.PatientSex = 'M'
        dataset.PatientName = 'LAST^FIRST^MIDDLE'

        original_patient_name = dataset.PatientName

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_patient_name = dataset.PatientName

        assert new_patient_name != original_patient_name
        assert (new_patient_name.split('^')[LAST]
                in PNAnonymizer._last_names)
        assert (new_patient_name.split('^')[FIRST]
                in PNAnonymizer._male_first_names)
        assert (new_patient_name.split('^')[MIDDLE]
                in PNAnonymizer._all_first_names)


def test_sex_other_patient_name_gets_anonymized():
    with load_test_instance() as dataset:
        dataset.PatientSex = 'O'
        dataset.PatientName = 'LAST^FIRST^MIDDLE'

        original_patient_name = dataset.PatientName

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_patient_name = dataset.PatientName

        assert new_patient_name != original_patient_name
        assert (new_patient_name.split('^')[LAST]
                in PNAnonymizer._last_names)
        assert (new_patient_name.split('^')[FIRST]
                in PNAnonymizer._all_first_names)
        assert (new_patient_name.split('^')[MIDDLE]
                in PNAnonymizer._all_first_names)


def load_dcm(filename):
    script_dir = os.path.dirname(__file__)
    return pydicom.dcmread(os.path.join(script_dir, filename))

import os
import datetime
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

    dataset.OperatorsName = "OPERATOR^FIRST^MIDDLE"
    dataset.NameOfPhysiciansReadingStudy = "READING^FIRST^MIDDLE"
    dataset.PerformingPhysicianName = "PERFORMING^FIRST^MIDDLE"
    dataset.ReferringPhysicianName = "REFERRING^FIRST^MIDDLE"
    dataset.RequestingPhysician = "REQUESTING^FIRST^MIDDLE"
    dataset.ResponsiblePerson = "RESPONSIBLE^FIRST^MIDDLE"
    dataset.PatientBirthName = "PBN",
    dataset.PatientMotherBirthName = "PMBN",

    dataset.PatientAddress = '10 REAL STREET'
    dataset.RegionOfResidence = 'BROAD COVE'
    dataset.CountryOfResidence = 'GERMANY'

    dataset.IssuerOfPatientID = "ISSUEROFPATIENTID"
    dataset.OtherPatientIDs = 'OTHERPATIENTID'
    dataset.PerformedProcedureStepID = 'PERFORMEDID'
    dataset.ScheduledProcedureStepID = 'SCHEDULEDID'

    dataset.Occupation = "VIGILANTE"
    dataset.PatientInsurancePlanCodeSequence = [
        code("VALUE", "DESIGNATOR", "MEANING")]
    dataset.MilitaryRank = "YEOMAN"
    dataset.BranchOfService = "COAST GUARD"
    dataset.PatientTelephoneNumbers = "123-456-7890"
    dataset.PatientTelecomInformation = "123-456-7890"
    dataset.PatientReligiousPreference = "PRIVATE"
    dataset.MedicalRecordLocator = "FILING CABINET 1"
    dataset.ReferencedPatientPhotoSequence = [referenced_photo_item()]
    dataset.ResponsibleOrganization = "RESPONSIBLE ORGANIZATION"

    other_patient_id_item0 = pydicom.dataset.Dataset()
    other_patient_id_item0.PatientID = "opi-0-ID"
    other_patient_id_item0.IssuerOfPatientID = "ISSUER"
    other_patient_id_item1 = pydicom.dataset.Dataset()
    other_patient_id_item1.PatientID = "opi-1-ID"
    other_patient_id_item1.IssuerOfPatientID = "ISSUER"
    dataset.OtherPatientIDsSequence = pydicom.sequence.Sequence(
        [other_patient_id_item0, other_patient_id_item1]
    )

    request_attribute_item = pydicom.dataset.Dataset()
    request_attribute_item.RequestedProcedureID = "rai-0-REQUESTEDID"
    request_attribute_item.ScheduledProcedureStepID = "rai-0-SCHEDULEDID"
    dataset.RequestAttributesSequence = pydicom.sequence.Sequence(
        [request_attribute_item]
    )

    dataset.InstitutionName = "INSTITUTIONNAME"
    dataset.InstitutionAddress = "INSTITUTIONADDRESS"
    dataset.InstitutionalDepartmentName = "INSTITUTIONALDEPARTMENTNAME"
    dataset.StationName = "STATIONNAME"

    dataset.RequestingService = "REQESTINGSERVICE"
    dataset.CurrentPatientLocation = "PATIENTLOCATION"

    return dataset


def code(value, designator, meaning):
    code_ds = pydicom.dataset.Dataset()
    code_ds.CodeValue = value
    code_ds.CodingSchemeDesignator = designator
    code_ds.CodeMeaning = meaning
    return code_ds


def referenced_photo_item():
    referenced_sop_item = pydicom.dataset.Dataset()
    referenced_sop_item.ReferencedSOPClassUID = "2.3.4.5.6.7"
    referenced_sop_item.ReferencedSOPInstanceUID = "2.3.4.5.6.7.1.2.3"

    item = pydicom.dataset.Dataset()
    item.TypeOfInstances = "DICOM"
    item.StudyInstanceUID = "1.2.3.4.5.6"
    item.SeriesInstanceUID = "1.2.3.4.5.6.1"
    item.ReferencedSOPSequence = [referenced_sop_item]

    return item


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


@pytest.mark.parametrize('element_path', [
    'AccessionNumber',
    'IssuerOfPatientID',
    'OtherPatientIDs',
    'OtherPatientIDsSequence[0].PatientID',
    'OtherPatientIDsSequence[0].IssuerOfPatientID',
    'OtherPatientIDsSequence[1].PatientID',
    'OtherPatientIDsSequence[1].IssuerOfPatientID',
    'PatientID',
    'PerformedProcedureStepID',
    'RequestAttributesSequence[0].RequestedProcedureID',
    'RequestAttributesSequence[0].ScheduledProcedureStepID',
    'ScheduledProcedureStepID',
    'StudyID',
])
def test_ids_are_anonymized(element_path):
    with load_test_instance() as dataset:

        original = eval('dataset.' + element_path)
        print 'original', original
        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = eval('dataset.' + element_path)

        assert actual != original


@pytest.mark.parametrize('number_of_ids', [1, 2, 3])
def test_other_patient_ids_anonymized_to_same_number_of_ids(number_of_ids):
    with load_test_instance() as dataset:

        original = ['ID' + str(i) for i in range(1, number_of_ids + 1)]
        dataset.OtherPatientIDs = original

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = dataset.OtherPatientIDs

        assert actual != original
        assert len(set(actual)) == number_of_ids


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


@pytest.mark.parametrize('number_of_names', [1, 2, 3])
def test_other_patient_names_anonymized_to_same_number_of_names(number_of_names):
    with load_test_instance() as dataset:

        original = ['NAME' + str(i) for i in range(1, number_of_names + 1)]
        dataset.OtherPatientNames = original

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = dataset.OtherPatientNames

        assert actual != original
        assert len(set(actual)) == number_of_names


@pytest.mark.parametrize('element_path', [
    'NameOfPhysiciansReadingStudy',
    'OperatorsName',
    'PatientBirthName',
    'PatientMotherBirthName',
    'PerformingPhysicianName',
    'ReferringPhysicianName',
    'RequestingPhysician',
    'ResponsiblePerson',
])
def test_non_patient_names_get_anonymized(element_path):
    with load_test_instance() as dataset:
        original_name = eval('dataset.' + element_path)
        assert original_name

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_name = eval('dataset.' + element_path)
        assert new_name != original_name


def test_patient_address_gets_anonymized():
    with load_test_instance() as dataset:
        original_address = dataset.PatientAddress
        original_region = dataset.RegionOfResidence
        original_country = dataset.CountryOfResidence

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_address = dataset.PatientAddress
        new_region = dataset.RegionOfResidence
        new_country = dataset.CountryOfResidence

        assert new_address != original_address
        assert new_region != original_region
        assert new_country != original_country


@pytest.mark.parametrize('element_name',
                         [
                             "Occupation",
                             "PatientInsurancePlanCodeSequence",
                             "MilitaryRank",
                             "BranchOfService",
                             "PatientTelephoneNumbers",
                             "PatientTelecomInformation",
                             "PatientReligiousPreference",
                             "MedicalRecordLocator",
                             "ReferencedPatientPhotoSequence",
                             "ResponsibleOrganization",
                         ])
def test_extra_patient_attributes_are_removed(element_name):
    with load_test_instance() as dataset:
        assert element_name in dataset

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        assert element_name not in dataset


def test_equipment_gets_anonymized():
    with load_test_instance() as dataset:
        original_institution_name = dataset.InstitutionName
        original_institution_address = dataset.InstitutionAddress
        original_institutional_department_name = dataset.InstitutionalDepartmentName
        original_station_name = dataset.StationName

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_institution_name = dataset.InstitutionName
        new_institution_address = dataset.InstitutionAddress
        new_institutional_department_name = dataset.InstitutionalDepartmentName
        new_station_name = dataset.StationName

        assert new_institution_name != original_institution_name
        assert new_institution_address != original_institution_address
        assert new_institutional_department_name != original_institutional_department_name
        assert new_station_name != original_station_name


def test_requesting_service_gets_anonymized():
    with load_test_instance() as dataset:
        original = dataset.RequestingService

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = dataset.RequestingService

        assert actual != original


def test_current_patient_location_gets_anonymized():
    with load_test_instance() as dataset:
        original = dataset.CurrentPatientLocation

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = dataset.CurrentPatientLocation

        assert actual != original


@pytest.mark.parametrize("date_name",
                         [
                             "AcquisitionDate",
                             "ContentDate",
                             "InstanceCreationTime",
                             "PatientBirthDate",
                             "PerformedProcedureStepStartDate",
                             "SeriesDate",
                             "StudyDate",
                         ])
def test_dates_and_times_get_anonymized_when_both_are_present(date_name):
    time_name = date_name[:-4] + "Time"

    original_datetime = datetime.datetime(1974, 11, 3, 12, 15, 58)
    original_date_string = original_datetime.strftime("%Y%m%d")
    original_time_string = original_datetime.strftime("%H%M%S")

    with load_test_instance() as dataset:
        setattr(dataset, date_name, original_date_string)
        setattr(dataset, time_name, original_time_string)

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_date_string = getattr(dataset, date_name)
        new_time_string = getattr(dataset, time_name)

    assert ((new_date_string, new_time_string) !=
            (original_date_string, original_time_string))


def test_date_gets_anonymized_when_there_is_no_time():
    with load_test_instance() as dataset:
        dataset.PatientBirthDate = original_birth_date = "20010401"
        assert 'PatientBirthTime' not in dataset

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_date_string = dataset.PatientBirthDate

    assert new_date_string != original_birth_date
    assert 'PatientBirthTime' not in dataset


@pytest.mark.parametrize("birth_date",
                         [
                             "20180202",
                             "199901",
                             "1983",
                         ])
def test_date_gets_anonymized_when_date_has_various_lengths(birth_date):
    with load_test_instance() as dataset:
        dataset.PatientBirthDate = birth_date
        dataset.PatientBirthTime = original_birth_time = "123456"

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_date_string = dataset.PatientBirthDate
        new_time_string = dataset.PatientBirthTime

    assert new_date_string != birth_date
    assert len(new_date_string) == len(birth_date)
    assert new_time_string[2:] == original_birth_time[2:]
    assert len(new_time_string) == len(original_birth_time)


@pytest.mark.parametrize("birth_time",
                         [
                             "",
                             "07",
                             "0911",
                             "131517",
                             "192123.1",
                             "192123.12",
                             "192123.123",
                             "192123.1234",
                             "192123.12345",
                             "192123.123456",
                         ])
def test_date_gets_anonymized_when_time_has_various_lengths(birth_time):
    with load_test_instance() as dataset:
        dataset.PatientBirthDate = original_birth_date = "20010401"
        dataset.PatientBirthTime = birth_time

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_date_string = dataset.PatientBirthDate
        new_time_string = dataset.PatientBirthTime

    assert new_date_string != original_birth_date
    assert len(new_date_string) == len(original_birth_date)
    assert new_time_string[2:] == birth_time[2:]
    assert len(new_time_string) == len(birth_time)


@pytest.mark.parametrize("datetime_name",
                         [
                             "AcquisitionDateTime",
                             "FrameReferenceDateTime",
                             "FrameAcquisitionDateTime",
                             "StartAcquisitionDateTime",
                             "EndAcquisitionDateTime",
                             "PerformedProcedureStepStartDateTime",
                             "PerformedProcedureStepEndDateTime",
                         ])
def test_datetime_gets_anonymized(datetime_name):
    original_datetime = datetime.datetime(1974, 11, 3, 12, 15, 58)
    original_datetime_string = original_datetime.strftime("%Y%m%d%H%M%S")

    with load_test_instance() as dataset:
        setattr(dataset, datetime_name, original_datetime_string)

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_datetime_string = getattr(dataset, datetime_name)

    assert new_datetime_string != original_datetime_string


@pytest.mark.parametrize("acquisition_datetime",
                         [
                             "1947",
                             "194711",
                             "19471103",
                             "1947110307",
                             "194711030911",
                             "19471103131517",
                             "19471103192123.1",
                             "19471103192123.12",
                             "19471103192123.123",
                             "19471103192123.1234",
                             "19471103192123.12345",
                             "19471103192123.123456",
                         ])
def test_datetime_of_various_lengths_gets_anonymized(acquisition_datetime):
    with load_test_instance() as dataset:
        dataset.AcquisitionDateTime = acquisition_datetime

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_datetime_string = dataset.AcquisitionDateTime

    assert new_datetime_string != acquisition_datetime
    assert len(new_datetime_string) == len(acquisition_datetime)


def load_dcm(filename):
    script_dir = os.path.dirname(__file__)
    return pydicom.dcmread(os.path.join(script_dir, filename))

import os
import pydicom
from pydicom.data import get_testdata_files


def load_patient1_study1_series1_instance1():
    dataset = load_minimal_instance()
    dataset.PatientAddress = "123 Fake Street"
    dataset.PatientBirthDate = "19830213"
    dataset.PatientBirthTime = "12:00:00"

    dataset.RequestingPhysician = "REQUESTING^FIRST^MIDDLE"
    dataset.RequestingService = "REQESTINGSERVICE"
    dataset.PerformingPhysicianName = "PERFORMING^FIRST^MIDDLE"
    dataset.ReferringPhysicianName = "REFERRING^FIRST^MIDDLE"

    dataset.InstitutionalDepartmentName = "INSTITUTIONALDEPARTMENTNAME"

    dataset.RequestedProcedureID = "rai-0-REQUESTEDID"
    request_attribute_item = pydicom.dataset.Dataset()
    request_attribute_item.RequestedProcedureID = dataset.RequestedProcedureID
    request_attribute_item.ScheduledProcedureStepID = "rai-0-SCHEDULEDID"
    dataset.RequestAttributesSequence = pydicom.sequence.Sequence(
        [request_attribute_item]
    )
    dataset.PerformedProcedureStepID = 'PERFORMEDID'
    dataset.ScheduledProcedureStepID = 'SCHEDULEDID'
    dataset.StationName = "STATIONNAME1"

    _align_secondary_patient_attributes(dataset)
    return dataset


def load_patient2_study1_series1_instance1():
    dataset = load_patient1_study1_series1_instance1()
    _set_patient2_attributes(dataset)
    return dataset


def load_minimal_instance():
    return load_dcm(get_testdata_files('MR_small.dcm')[0])


def load_test_instance():
    dataset = load_minimal_instance()
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


def load_dcm(filename):
    script_dir = os.path.dirname(__file__)
    return pydicom.dcmread(os.path.join(script_dir, filename))


def _set_patient2_attributes(dataset):
    dataset.PatientAddress = "124 Fake Street"
    dataset.PatientBirthDate = "19830214"
    dataset.PatientBirthTime = "13:14:00"
    dataset.PatientID = "4MR2"
    dataset.PatientName = "CompressedSamples^MR2"
    _align_secondary_patient_attributes(dataset)
    _set_study2_attributes(dataset)


def _align_secondary_patient_attributes(dataset):
    dataset.OtherPatientIDs = "OTH" + dataset.PatientID
    dataset.OtherPatientIDsSequence = [pydicom.dataset.Dataset()]
    dataset.OtherPatientIDsSequence[0].PatientID = "OTHSEQ" + dataset.PatientID

    dataset.OtherPatientNames = "Other" + dataset.PatientName
    dataset.PatientBirthName = "Birth" + dataset.PatientName
    dataset.PatientMotherBirthName = "Mother" + dataset.PatientName
    dataset.ResponsiblePerson = "Responsible" + dataset.PatientName


def _set_study2_attributes(dataset):
    dataset.StudyId = "4MR2"
    dataset.StudyDate = "20040827"
    dataset.StudyTime = "145012"
    dataset.StudyInstanceUID = "1.3.6.1.4.1.5962.1.2.4.20040827145012.5458"
    _set_series2_attributes(dataset)


def _set_series2_attributes(dataset):
    dataset.SeriesInstanceUID = "1.3.6.1.4.1.5962.1.3.4.1.20040827145012.5458"
    dataset.FrameOfReferenceUID = "1.3.6.1.4.1.5962.1.4.4.1.20040827145012.5458"
    dataset.SeriesDate = "20040827"
    dataset.SeriesTime = "145012"
    dataset.StationName = "STATIONNAME2"
    _set_instance2_attributes(dataset)


def _set_instance2_attributes(dataset):
    dataset.file_meta.MediaStorageSOPInstanceUID = "1.3.6.1.4.1.5962.1.1.4.1.1.20040826185059.5458"
    dataset.InstanceCreationDate = "20040827"
    dataset.InstanceCreationTime = "185521"
    dataset.SOPInstanceUID = "1.3.6.1.4.1.5962.1.1.4.1.1.20040826185059.5458"

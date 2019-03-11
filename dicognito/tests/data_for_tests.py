import os
import datetime
import pydicom
from pydicom.data import get_testdata_files


def load_instance(patient_number=1, study_number=1, series_number=1, instance_number=1):
    dataset = load_minimal_instance()
    _set_patient_attributes(dataset, patient_number)
    _set_study_attributes(dataset, patient_number, study_number)
    _set_series_attributes(dataset, patient_number,
                           study_number, series_number)
    _set_instance_attributes(dataset, patient_number,
                             study_number, series_number, instance_number)
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


def _set_patient_attributes(dataset, patient_number):
    dataset.PatientAddress = str(123 + patient_number) + " Fake Street"
    dataset.PatientBirthDate = str(19830213 + patient_number)
    dataset.PatientBirthTime = "13:14:0" + str(patient_number)
    dataset.PatientID = "4MR" + str(patient_number)
    dataset.PatientName = "CompressedSamples^MR" + str(patient_number)
    dataset.OtherPatientIDs = "OTH" + dataset.PatientID
    dataset.OtherPatientIDsSequence = [pydicom.dataset.Dataset()]
    dataset.OtherPatientIDsSequence[0].PatientID = "OTHSEQ" + dataset.PatientID

    dataset.OtherPatientNames = "Other" + dataset.PatientName
    dataset.PatientBirthName = "Birth" + dataset.PatientName
    dataset.PatientMotherBirthName = "Mother" + dataset.PatientName
    dataset.ResponsiblePerson = "Responsible" + dataset.PatientName


def _set_study_attributes(dataset, patient_number, study_number):
    dataset.StudyID = ("STUDYFOR4MR" +
                       str(patient_number) + "." + str(study_number))
    dataset.AccessionNumber = "ACC" + dataset.StudyID
    dataset.StudyDate = (datetime.date(2004, patient_number, study_number)
                         .strftime("%Y%m%d"))
    dataset.StudyTime = (datetime.time(
        patient_number * 5 + study_number, 0, 0).strftime("%H%M%S"))
    dataset.StudyInstanceUID = ("1.3.6.1.4.1.5962.20040827145012.5458." +
                                str(patient_number) + "." + str(study_number))
    dataset.NameOfPhysiciansReadingStudy = "READING^FIRST^" + dataset.StudyID
    dataset.RequestingPhysician = "REQUESTING1^FIRST^" + dataset.StudyID
    dataset.ReferringPhysicianName = "REFERRING1^FIRST^" + dataset.StudyID


def _set_series_attributes(dataset, patient_number, study_number, series_number):
    series_suffix = "%(patient_number)-d%(study_number)-d%(series_number)d" % vars()
    dataset.SeriesInstanceUID = (dataset.StudyInstanceUID +
                                 "." + str(series_number))
    dataset.FrameOfReferenceUID = (dataset.SeriesInstanceUID +
                                   ".0." + str(series_number))
    dataset.PerformedProcedureStepID = "PERFSTEP" + series_suffix
    dataset.RequestedProcedureID = "REQSTEP" + series_suffix
    dataset.ScheduledProcedureStepID = "SCHEDSTEP" + series_suffix

    dataset.SeriesDate = dataset.StudyDate
    dataset.SeriesTime = datetime.time(
        patient_number, study_number, series_number
    ).strftime("%H%M%S")
    dataset.StationName = ("STATIONNAME" + str(patient_number) +
                           "." + str(study_number) + "." + str(series_number))
    dataset.OperatorsName = "OPERATOR^FIRST^" + series_suffix
    dataset.PerformingPhysicianName = "PERFORMING1^FIRST^" + series_suffix

    request_attribute_item = pydicom.dataset.Dataset()
    request_attribute_item.RequestedProcedureID = dataset.RequestedProcedureID
    request_attribute_item.ScheduledProcedureStepID = dataset.ScheduledProcedureStepID
    dataset.RequestAttributesSequence = pydicom.sequence.Sequence(
        [request_attribute_item]
    )

    dataset.InstitutionName = "INSTITUTIONNAME" + series_suffix
    dataset.InstitutionAddress = "INSTITUTIONADDRESS" + series_suffix
    dataset.InstitutionalDepartmentName = "INSTITUTIONALDEPARTMENTNAME" + series_suffix
    dataset.StationName = "STATIONNAME" + series_suffix


def _set_instance_attributes(dataset, patient_number, study_number, series_number, instance_number):
    dataset.SOPInstanceUID = (dataset.SeriesInstanceUID +
                              "." + str(instance_number))
    dataset.file_meta.MediaStorageSOPInstanceUID = dataset.SOPInstanceUID
    dataset.InstanceCreationDate = dataset.SeriesDate
    dataset.InstanceCreationTime = datetime.time(
        patient_number, study_number, 7*series_number + instance_number
    ).strftime("%H%M%S")

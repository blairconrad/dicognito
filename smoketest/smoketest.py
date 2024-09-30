import os

import pydicom
from pydicom.data import get_testdata_files

import dicognito.anonymizer


def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))

    filename = get_testdata_files("MR_small.dcm")[0]
    ds = pydicom.dcmread(filename)

    ds.OtherPatientIDs = ["OPID1", "OPID2"]

    ds.PatientAddress = "10 REAL STREET"
    ds.RegionOfResidence = "BROAD COVE"
    ds.CountryOfResidence = "GERMANY"

    ds.PatientBirthDate = "19670219"
    ds.PatientBirthTime = "2315"

    ds.save_as(script_dir + "/original.dcm")
    with open(script_dir + "/original.txt", "wb") as f:
        f.write(str(ds).encode("utf-8"))

    dicognito.anonymizer.Anonymizer().anonymize(ds)

    ds.save_as(script_dir + "/anonymizeds.dcm")
    with open(script_dir + "/anonymized.txt", "wb") as f:
        f.write(str(ds).encode("utf-8"))


if __name__ == "__main__":
    main()

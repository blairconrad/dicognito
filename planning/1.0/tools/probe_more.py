"""
Probe issuer collapse and empty values.

Run from the repository root: uv run python planning/1.0/tools/probe_more.py
"""

import warnings

from pydicom.dataset import Dataset

from dicognito.anonymizer import Anonymizer

warnings.simplefilter("ignore")
a = Anonymizer(seed="probe")
d1, d2 = Dataset(), Dataset()
for d, issuer in ((d1, "HOSP_A"), (d2, "HOSP_B")):
    d.ensure_file_meta()
    d.PatientID = "123"
    d.IssuerOfPatientID = issuer
    d.PatientName = "SMITH^ANN" if issuer == "HOSP_A" else "JONES^BOB"
    a.anonymize(d)
print("issuer A:", d1.PatientID, d1.IssuerOfPatientID, d1.PatientName)
print("issuer B:", d2.PatientID, d2.IssuerOfPatientID, d2.PatientName)

d = Dataset()
d.ensure_file_meta()
d.OtherPatientNames = ["", "DOE^JANE"]
try:
    a.anonymize(d)
    print("PN multi with empty component:", list(d.OtherPatientNames))
except TypeError as ex:
    print("PN multi with empty component: TypeError", str(ex).splitlines()[-1])

d = Dataset()
d.ensure_file_meta()
d.AccessionNumber = ""
e = Dataset()
e.ensure_file_meta()
e.AccessionNumber = ""
a.anonymize(d)
a.anonymize(e)
print("two empty accession numbers:", d.AccessionNumber, e.AccessionNumber)

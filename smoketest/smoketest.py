import os
import pydicom
from pydicom.data import get_testdata_files

script_dir = os.path.dirname(os.path.realpath(__file__))

filename = get_testdata_files("MR_small.dcm")[0]
ds = pydicom.dcmread(filename)

ds.OtherPatientIDs = ['OPID1', 'OPID2']

ds.PatientAddress = '10 REAL STREET'
ds.RegionOfResidence = 'BROAD COVE'
ds.CountryOfResidence = 'GERMANY'

ds.PatientBirthDate = '19670219'
ds.PatientBirthTime = '2315'

ds.save_as(script_dir + '/original.dcm')
with file(script_dir + '/original.txt', 'wb') as f:
    f.write(str(ds))

import dicognito.anonymizer
dicognito.anonymizer.Anonymizer().anonymize(ds)

ds.save_as(script_dir + '/anonymizeds.dcm')
with file(script_dir + '/anonymized.txt', 'wb') as f:
    f.write(str(ds))

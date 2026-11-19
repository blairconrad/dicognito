"""
Targeted probes of dicognito edge cases and suspected inconsistencies.

Run from the repository root: uv run python planning/1.0/tools/probe_edges.py
"""

import warnings

import pydicom
from pydicom.datadict import DicomDictionary, keyword_for_tag
from pydicom.dataset import Dataset
from pydicom.sequence import Sequence
from pydicom.uid import UID_dictionary

from dicognito.anonymizer import Anonymizer
from dicognito.value_keeper import ValueKeeper

warnings.simplefilter("ignore")


def new_ds(**kw):
    ds = Dataset()
    ds.ensure_file_meta()
    for k, v in kw.items():
        setattr(ds, k, v)
    return ds


def anon(ds, seed="probe", **kw):
    Anonymizer(seed=seed, **kw).anonymize(ds)
    return ds


def section(title):
    print(f"\n=== {title}")


section("1. Same physician, patients of different sex")
f = anon(new_ds(PatientSex="F", ReferringPhysicianName="WELBY^MARCUS"))
m = anon(new_ds(PatientSex="M", ReferringPhysicianName="WELBY^MARCUS"))
n = anon(new_ds(ReferringPhysicianName="WELBY^MARCUS"))
print("F:", f.ReferringPhysicianName, "| M:", m.ReferringPhysicianName, "| none:", n.ReferringPhysicianName)

section("2. Same person name top-level vs in sequence item (patient F)")
item = Dataset()
item.PerformingPhysicianName = "HOUSE^GREGORY"
ds = new_ds(PatientSex="F", PerformingPhysicianName="HOUSE^GREGORY", PerformedProtocolCodeSequence=Sequence([item]))
anon(ds)
print("top:", ds.PerformingPhysicianName, "| item:", ds.PerformedProtocolCodeSequence[0].PerformingPhysicianName)

section("3. Name case/format variants")
for v in ("DOE^JOHN", "doe^john", "DOE^JOHN^^^", "DOE^JOHN ", "Doe^John=ドウ^ジョン"):
    print(repr(v), "->", anon(new_ds(PatientName=v)).PatientName)

section("4. Orphan TM (no DA) vs paired TM in same dataset")
ds = anon(new_ds(StudyDate="20200102", StudyTime="100000", AcquisitionTime="100500", SeriesTime="100200"))
print("StudyDate/Time:", ds.StudyDate, ds.StudyTime, "| SeriesTime (no SeriesDate):", ds.SeriesTime, "| AcquisitionTime (no date):", ds.AcquisitionTime)

section("5. Same date with and without time")
ds = anon(new_ds(StudyDate="20200102", StudyTime="230000", SeriesDate="20200102", ContentDate="20200102", ContentTime="010000"))
print("StudyDate+23h:", ds.StudyDate, ds.StudyTime, "| SeriesDate (no time):", ds.SeriesDate, "| ContentDate+01h:", ds.ContentDate, ds.ContentTime)

section("6. Empty values")
ds = anon(new_ds(AccessionNumber="", PatientID="", InstitutionName="", InstitutionalDepartmentName="", PatientName="", StudyDate="", StudyInstanceUID="", IssuerOfPatientID="", PatientAddress="", CurrentPatientLocation=""))
for k in ("AccessionNumber", "PatientID", "InstitutionName", "InstitutionAddress", "InstitutionalDepartmentName", "PatientName", "StudyDate", "StudyInstanceUID", "IssuerOfPatientID", "PatientAddress", "CurrentPatientLocation", "DeidentificationMethod", "PatientIdentityRemoved"):
    print(f"  {k}: {ds.get(k, '<absent>')!r}")

section("6b. None-valued (zero-length) ID element read from file")
ds = new_ds()
ds.add_new("PatientID", "LO", None)
try:
    anon(ds)
    print("  PatientID:", repr(ds.PatientID))
except Exception as e:  # noqa: BLE001
    print("  ERROR", type(e).__name__, e)

section("6c. Multi-valued ID with an empty component")
ds = anon(new_ds(OtherPatientIDs=["A1", ""]))
print("  OtherPatientIDs:", list(ds.OtherPatientIDs))

section("7. Invalid / partial date values")
for v in ("UNKNOWN", "2020", "20200230", "00000000", "20200102-20200105"):
    ds = new_ds()
    ds.add_new("StudyDate", "DA", v)
    try:
        anon(ds)
        print(f"  {v!r} ->", repr(ds.StudyDate))
    except Exception as e:  # noqa: BLE001
        print(f"  {v!r} -> ERROR {type(e).__name__}: {e}")
ds = new_ds()
ds.add_new("StudyDate", "DA", ["20200102", ""])
try:
    anon(ds)
    print("  multi with empty ->", ds.StudyDate)
except Exception as e:  # noqa: BLE001
    print("  multi with empty -> ERROR", type(e).__name__, e)
for v in ("20200102120000+0500", "2020", "20200102120000.123456-0300"):
    ds = anon(new_ds(AcquisitionDateTime=v))
    print(f"  DT {v!r} ->", ds.AcquisitionDateTime)

section("8. Equal original values in different ID attributes map to the same output")
ds = anon(new_ds(PatientID="12345", AccessionNumber="12345", StudyID="12345", StationName="12345"))
print("  ", ds.PatientID, ds.AccessionNumber, ds.StudyID, ds.StationName)

section("9. ID affixes")
for p, s in (("TEST", ""), ("ABCDEFGHIJKL", ""), ("ABCDEFGHIJKLMN", "XYZ")):
    ds = anon(new_ds(PatientID="1", AccessionNumber="2", StationName="CT01"), id_prefix=p, id_suffix=s)
    print(f"  prefix={p!r} suffix={s!r}:", ds.PatientID, ds.AccessionNumber, ds.StationName, "len", len(ds.AccessionNumber))

section("10. DeidentificationMethod dictionary VM")
print("  VM:", DicomDictionary[0x00120063][1])

section("11. UI attributes not ending in ClassUID or TransferSyntaxUID (would be replaced)")
skip = []
for tag, entry in sorted(DicomDictionary.items()):
    vr, vm, name, retired, kw = entry
    if vr == "UI" and not kw.endswith("ClassUID") and kw != "TransferSyntaxUID":
        skip.append(kw)
suspicious = [k for k in skip if any(s in k for s in ("Class", "Syntax", "Coding", "Scheme", "Context", "Template", "Mapping", "Private", "Creator", "Organization", "Codec", "Application", "Algorithm", "Implementation", "Classes", "Profile", "Resource"))]
print("  total UI keywords replaced:", len(skip))
print("  suspicious (likely well-known/registry UIDs):", suspicious)

section("11b. Well-known UID value in a 'replaceable' attribute")
ds = anon(new_ds(CodingSchemeUID="1.2.840.10008.2.16.4", ReferencedTransferSyntaxUIDInFile="1.2.840.10008.1.2.1", ContextGroupExtensionCreatorUID="1.2.3"))
print("  CodingSchemeUID:", ds.CodingSchemeUID, "| ReferencedTransferSyntaxUIDInFile:", ds.ReferencedTransferSyntaxUIDInFile)
print("  is 1.2.840.10008.2.16.4 in pydicom UID_dictionary:", "1.2.840.10008.2.16.4" in UID_dictionary)

section("12. SR content items")
items = []
for vt, attr, vr, val in (("PNAME", "PersonName", "PN", "DOE^JANE"), ("DATE", "Date", "DA", "20200102"), ("TIME", "Time", "TM", "101010"), ("DATETIME", "DateTime", "DT", "20200102101010"), ("UIDREF", "UID", "UI", "1.2.3.4"), ("TEXT", "TextValue", "UT", "Patient Jane Doe seen 2020-01-02")):
    it = Dataset()
    it.ValueType = vt
    it.add_new(attr, vr, val)
    items.append(it)
ds = anon(new_ds(ContentSequence=Sequence(items)))
for it in ds.ContentSequence:
    elem = [e for e in it if e.keyword != "ValueType"][0]
    print(f"  {it.ValueType}: {elem.keyword} = {elem.value!r}")

section("13. Private elements with explicit VR")
ds = new_ds()
ds.add_new(0x00090010, "LO", "ACME 1.0")
ds.add_new(0x00091001, "PN", "PRIVATE^NAME")
ds.add_new(0x00091002, "LO", "PRIVATE NAME IN LO")
ds.add_new(0x00091003, "UI", "1.2.3.4.5")
ds.add_new(0x00091004, "DA", "20200102")
ds.add_new(0x00091005, "UN", b"DOE^JOHN")
anon(ds)
for t in (0x00091001, 0x00091002, 0x00091003, 0x00091004, 0x00091005):
    print(f"  {pydicom.tag.Tag(t)} {ds[t].VR}: {ds[t].value!r}")

section("14. Overlay / curve / retrieve URL / AE titles left in place")
ds = new_ds(RetrieveURL="https://pacs.hospital.example/wado?studyUID=1.2.3", RetrieveAETitle="HOSPPACS", StationAETitle="CT_ROOM_3")
ds.add_new(0x60004000, "LT", "overlay comment with name")
ds.add_new(0x50002500, "LO", "curve label")
anon(ds)
print("  ", ds.RetrieveURL, ds.RetrieveAETitle, ds.StationAETitle, ds[0x60004000].value, ds[0x50002500].value)

section("15. InstitutionName adds InstitutionAddress; keep interactions")
ds = anon(new_ds(InstitutionName="MERCY"))
print("  added address:", ds.get("InstitutionAddress", "<absent>"))
a = Anonymizer(seed="probe")
a.add_element_handler(ValueKeeper("StudyTime"))
ds = new_ds(StudyDate="20200102", StudyTime="100000")
a.anonymize(ds)
print("  keep StudyTime only:", ds.StudyDate, ds.StudyTime)
a = Anonymizer(seed="probe")
a.add_element_handler(ValueKeeper("PatientID"))
item = Dataset()
item.PatientID = "MRN1"
ds = new_ds(PatientID="MRN1", OtherPatientIDsSequence=Sequence([item]))
a.anonymize(ds)
print("  keep PatientID (also in sequence):", ds.PatientID, ds.OtherPatientIDsSequence[0].PatientID)

section("16. Re-anonymizing output (idempotence)")
ds = anon(new_ds(PatientID="MRN1", StudyDate="20200102", PatientName="DOE^JOHN"))
first = (ds.PatientID, ds.StudyDate, str(ds.PatientName), list(ds.DeidentificationMethod) if isinstance(ds.DeidentificationMethod, list) else ds.DeidentificationMethod)
anon(ds)
print("  first:", first, "| second:", (ds.PatientID, ds.StudyDate, str(ds.PatientName), ds.DeidentificationMethod))

section("17. Date offset range for many seeds (days)")
import datetime as dt
offs = []
for i in range(2000):
    d = anon(new_ds(StudyDate="20200601"), seed=str(i)).StudyDate
    offs.append((dt.date(2020, 6, 1) - dt.date(int(d[:4]), int(d[4:6]), int(d[6:]))).days)
print("  min", min(offs), "max", max(offs))

section("18. PatientAge vs shifted birth date")
ds = anon(new_ds(PatientBirthDate="19800615", StudyDate="20200601", PatientAge="039Y"))
print("  ", ds.PatientBirthDate, ds.StudyDate, ds.PatientAge)

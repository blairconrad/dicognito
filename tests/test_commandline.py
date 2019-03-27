import sys
import os.path
import shutil
import dicognito.__main__
from .data_for_tests import load_dcm


def setup_module(module):
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "data")
    orig_dir = os.path.join(base_dir, "orig_data")
    if os.path.isdir(data_dir):
        shutil.rmtree(data_dir)
    shutil.copytree(orig_dir, data_dir)


def test_overwrite_files(capsys):
    test_name = get_test_name()
    orig_dataset = read_original_file(test_name, "p01_s01_s01_i01.dcm")
    assert "CompressedSamples^MR1" == orig_dataset.PatientName

    run_dicognito(capsys, path_to("p*"))

    anon_dataset = read_file(test_name, "p01_s01_s01_i01.dcm")
    assert anon_dataset.PatientName != orig_dataset.PatientName


def test_ignores_file_that_do_not_match_glob(capsys):
    test_name = get_test_name()
    orig_dataset = read_original_file(test_name, "np01_s01_s01_i01.dcm")
    assert "CompressedSamples^MR1" == orig_dataset.PatientName

    run_dicognito(capsys, path_to("p*"))

    anon_dataset = read_file(test_name, "np01_s01_s01_i01.dcm")
    assert anon_dataset.PatientName == orig_dataset.PatientName


def test_summary_mixed_files_reports_on_each_study(capsys):
    expected = """\
Accession Number Patient ID       Patient Name
---------------- ----------       ------------
DRVN05NEDUYD     2S183ZNON7HU     RICHMOND^MARCY^NITA
8NZGNEJWE7QA     NPC1XHSJT51Z     MORROW^SUSANNA^LUCIEN
SXJXM4HE90EO     NPC1XHSJT51Z     MORROW^SUSANNA^LUCIEN
"""
    actual = run_dicognito(capsys, path_to("p*"))

    assert expected == actual


def test_summary_with_quiet_no_report(capsys):
    actual = run_dicognito(capsys, path_to("p*"), "--quiet")
    expected = ""
    assert expected == actual


def test_directory_is_recursed(capsys):
    test_name = get_test_name()
    orig_dataset1 = read_original_file(test_name, "p01_s01_s01_i01.dcm")
    orig_dataset2 = read_original_file(test_name, "a", "b", "p01_s02_s01_i01.dcm")
    assert "CompressedSamples^MR1" == orig_dataset1.PatientName
    assert "CompressedSamples^MR1" == orig_dataset2.PatientName

    run_dicognito(capsys, path_to(""))

    anon_dataset1 = read_file(test_name, "p01_s01_s01_i01.dcm")
    anon_dataset2 = read_file(test_name, "a", "b", "p01_s02_s01_i01.dcm")
    assert orig_dataset1.PatientName != anon_dataset1.PatientName
    assert orig_dataset2.PatientName != anon_dataset2.PatientName


def test_non_dicom_files_ignored(capsys):
    test_name = get_test_name()
    orig_dataset = read_original_file(test_name, "p01_s01_s01_i01.dcm")
    assert "CompressedSamples^MR1" == orig_dataset.PatientName

    run_dicognito(capsys, path_to(""))

    anon_dataset = read_file(test_name, "p01_s01_s01_i01.dcm")
    assert orig_dataset.PatientName != anon_dataset.PatientName


def get_test_name():
    depth = 1
    while True:
        frame = sys._getframe(depth)
        if frame.f_code.co_name.startswith("test"):
            return frame.f_code.co_name
        depth += 1


def path_to(end_of_path):
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, "data", get_test_name(), end_of_path)


def run_dicognito(capsys, *extra_args):
    dicognito.__main__.main(("--salt", "salt for test") + extra_args)
    (out, error) = capsys.readouterr()
    return out


def read_file(*directory_parts):
    return load_dcm(os.path.join("data", *directory_parts))


def read_original_file(*directory_parts):
    return load_dcm(os.path.join("orig_data", *directory_parts))

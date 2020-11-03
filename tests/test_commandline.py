import sys
import os.path
import shutil
import logging
import dicognito.__main__
from .data_for_tests import load_dcm

data_dir = None


def setup_module(module):
    base_dir = os.path.dirname(__file__)
    orig_dir = os.path.join(base_dir, "orig_data")

    global data_dir
    data_dir = os.path.join(base_dir, "..", "build", "data")
    if os.path.isdir(data_dir):
        shutil.rmtree(data_dir)
    shutil.copytree(orig_dir, data_dir)


def test_overwrite_files():
    test_name = get_test_name()
    orig_dataset = read_original_file(test_name, "p01_s01_s01_i01.dcm")
    assert "CompressedSamples^MR1" == orig_dataset.PatientName

    run_dicognito(path_to("p*"))

    anon_dataset = read_file(test_name, "p01_s01_s01_i01.dcm")
    assert anon_dataset.PatientName != orig_dataset.PatientName


def test_ignores_file_that_do_not_match_glob():
    test_name = get_test_name()
    orig_dataset = read_original_file(test_name, "np01_s01_s01_i01.dcm")
    assert "CompressedSamples^MR1" == orig_dataset.PatientName

    run_dicognito(path_to("p*"))

    anon_dataset = read_file(test_name, "np01_s01_s01_i01.dcm")
    assert anon_dataset.PatientName == orig_dataset.PatientName


def test_summary_mixed_files_reports_on_each_study(capsys):
    expected_output = """\
Accession Number Patient ID       Patient Name
---------------- ----------       ------------
HGED6DXQTO1F     DQFZ0HDKPYUX     JENSEN^KELLIE^PATRICK
XV266HDCGIOH     DQFZ0HDKPYUX     JENSEN^KELLIE^PATRICK
UUM68P1IJHBE     LXO0DMOPN7PV     BUCHANAN^ALBA^MADGE
"""
    run_dicognito(path_to("p*"))
    (actual_output, actual_error) = capsys.readouterr()

    assert expected_output == actual_output


def test_summary_with_quiet_no_report(capsys):
    expected_output = ""

    run_dicognito(path_to("p*"), "--quiet")
    (actual_output, actual_error) = capsys.readouterr()

    assert expected_output == actual_output


def test_summary_no_accession_number(capsys):
    expected_output = """\
Accession Number Patient ID       Patient Name
---------------- ----------       ------------
                 LXO0DMOPN7PV     BUCHANAN^ALBA^MADGE
"""
    run_dicognito(path_to("p*"))
    (actual_output, actual_error) = capsys.readouterr()

    assert expected_output == actual_output


def test_directory_is_recursed():
    test_name = get_test_name()
    orig_dataset1 = read_original_file(test_name, "p01_s01_s01_i01.dcm")
    orig_dataset2 = read_original_file(test_name, "a", "b", "p01_s02_s01_i01.dcm")
    assert "CompressedSamples^MR1" == orig_dataset1.PatientName
    assert "CompressedSamples^MR1" == orig_dataset2.PatientName

    run_dicognito(path_to(""))

    anon_dataset1 = read_file(test_name, "p01_s01_s01_i01.dcm")
    anon_dataset2 = read_file(test_name, "a", "b", "p01_s02_s01_i01.dcm")
    assert orig_dataset1.PatientName != anon_dataset1.PatientName
    assert orig_dataset2.PatientName != anon_dataset2.PatientName


def test_non_dicom_files_ignored(capsys):
    expected_error = ""

    test_name = get_test_name()
    orig_dataset = read_original_file(test_name, "p01_s01_s01_i01.dcm")
    assert "CompressedSamples^MR1" == orig_dataset.PatientName

    run_dicognito(path_to(""))
    (actual_output, actual_error) = capsys.readouterr()

    anon_dataset = read_file(test_name, "p01_s01_s01_i01.dcm")
    assert orig_dataset.PatientName != anon_dataset.PatientName
    assert expected_error == actual_error


def test_non_dicom_files_logged_at_info(caplog):
    expected_error = "not_a_dicom_file.txt appears not to be DICOM. Skipping."

    test_name = get_test_name()
    orig_dataset = read_original_file(test_name, "p01_s01_s01_i01.dcm")
    assert "CompressedSamples^MR1" == orig_dataset.PatientName

    # py.test configures the logs itself, so setting the log level in the command
    # doesn't work. Instead, use caplog to set the level.
    caplog.set_level(logging.INFO)
    run_dicognito(path_to(""))

    anon_dataset = read_file(test_name, "p01_s01_s01_i01.dcm")
    assert orig_dataset.PatientName != anon_dataset.PatientName

    log_record = caplog.records[0]
    assert log_record.levelname == "INFO"
    assert log_record.getMessage().endswith(expected_error)


def test_creates_output_directory_when_missing():
    run_dicognito(path_to(""), "--output-dir", path_to("new_dir"))

    assert os.path.isdir(path_to("new_dir"))


def test_preserves_existing_source_files_when_writing_to_output_directory():
    run_dicognito(path_to("p01_s01_s01_i01.dcm"), "--output-dir", path_to())

    orig_dataset = read_original_file(get_test_name(), "p01_s01_s01_i01.dcm")
    assert orig_dataset.SOPInstanceUID == "1.3.6.1.4.1.5962.20040827145012.5458.1.1.1.1"


def test_writes_file_as_sop_instance_uid_in_output_directory():
    run_dicognito(path_to("p01_s01_s01_i01.dcm"), "--output-dir", path_to("new_dir"))

    all_output_files = os.listdir(path_to("new_dir"))
    assert len(all_output_files) == 1

    dataset = read_file(get_test_name(), "new_dir", all_output_files[0])
    assert all_output_files[0] == dataset.SOPInstanceUID + ".dcm"


def test_retains_existing_files_in_output_directory():
    run_dicognito(path_to("p01_s01_s01_i01.dcm"), "--output-dir", path_to())

    all_output_files = os.listdir(path_to())
    assert len(all_output_files) == 2
    assert "p01_s01_s01_i01.dcm" in all_output_files


def test_writes_deflated_file_correctly():
    run_dicognito(path_to("CT_small_deflated.dcm"), "--output-dir", path_to("new_dir"))

    output_file_name = os.listdir(path_to("new_dir"))[0]

    read_file(get_test_name(), "new_dir", output_file_name)


def get_test_name():
    depth = 1
    while True:
        frame = sys._getframe(depth)
        if frame.f_code.co_name.startswith("test"):
            return frame.f_code.co_name
        depth += 1


def path_to(*end_of_path):
    return os.path.join(data_dir, get_test_name(), *end_of_path)


def run_dicognito(*extra_args):
    dicognito.__main__.main(("--seed", "") + extra_args)


def read_file(*directory_parts):
    return load_dcm(data_dir, *directory_parts)


def read_original_file(*directory_parts):
    return load_dcm("orig_data", *directory_parts)

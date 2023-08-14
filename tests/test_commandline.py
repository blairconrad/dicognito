import logging
import os.path
import shutil
import sys

import dicognito.__main__
import pydicom
import pytest

from .data_for_tests import load_dcm

data_dir = ""


def setup_module():
    base_dir = os.path.dirname(__file__)
    orig_dir = os.path.join(base_dir, "orig_data")

    global data_dir
    data_dir = os.path.join(base_dir, "..", "build", "data")
    if os.path.isdir(data_dir):
        shutil.rmtree(data_dir)
    shutil.copytree(orig_dir, data_dir)


def test_implicit_in_place_warns_but_anonymizes(caplog):
    test_name = get_test_name()
    orig_dataset = read_original_file(test_name, "p01_s01_s01_i01.dcm")
    assert orig_dataset.PatientName == "CompressedSamples^MR1"

    run_dicognito(path_to(""))

    log_record = [log for log in caplog.records if log.levelname == "WARNING"][0]
    assert (
        "Neither --output-directory/-o nor --in-place/-i were specified. This will be an error in the future."
        in log_record.getMessage()
    )

    run_dicognito(path_to("p*"))

    anon_dataset = read_file(test_name, "p01_s01_s01_i01.dcm")
    assert anon_dataset.PatientName != orig_dataset.PatientName


def test_in_place_overwrites_files():
    test_name = get_test_name()
    orig_dataset = read_original_file(test_name, "p01_s01_s01_i01.dcm")
    assert orig_dataset.PatientName == "CompressedSamples^MR1"

    run_dicognito(path_to("p*"), "--in-place")

    anon_dataset = read_file(test_name, "p01_s01_s01_i01.dcm")
    assert anon_dataset.PatientName != orig_dataset.PatientName


def test_in_place_short_form_overwrites_files():
    test_name = get_test_name()
    orig_dataset = read_original_file(test_name, "p01_s01_s01_i01.dcm")
    assert orig_dataset.PatientName == "CompressedSamples^MR1"

    run_dicognito(path_to("p*"), "-i")

    anon_dataset = read_file(test_name, "p01_s01_s01_i01.dcm")
    assert anon_dataset.PatientName != orig_dataset.PatientName


def test_ignores_file_that_do_not_match_glob():
    test_name = get_test_name()
    orig_dataset = read_original_file(test_name, "np01_s01_s01_i01.dcm")
    assert orig_dataset.PatientName == "CompressedSamples^MR1"

    run_dicognito(path_to("p*"))

    anon_dataset = read_file(test_name, "np01_s01_s01_i01.dcm")
    assert anon_dataset.PatientName == orig_dataset.PatientName


def test_summary_mixed_files_reports_on_each_study(capsys):
    expected_output = """\
| Accession Number |  Patient ID  |     Patient Name      |
| ---------------- | ------------ | --------------------- |
| 028EY1JNTTP8     | DQFZ0HDKPYUX | JENSEN^KELLIE^PATRICK |
| 5VIGINLZ0LPZ     | DQFZ0HDKPYUX | JENSEN^KELLIE^PATRICK |
| PYDV44HEDN1E     | LXO0DMOPN7PV | BUCHANAN^ALBA^MADGE   |
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
| Accession Number |  Patient ID  |    Patient Name     |
| ---------------- | ------------ | ------------------- |
|                  | LXO0DMOPN7PV | BUCHANAN^ALBA^MADGE |
"""
    run_dicognito(path_to("p*"))
    (actual_output, actual_error) = capsys.readouterr()

    assert expected_output == actual_output


def test_directory_is_recursed():
    test_name = get_test_name()
    orig_dataset1 = read_original_file(test_name, "p01_s01_s01_i01.dcm")
    orig_dataset2 = read_original_file(test_name, "a", "b", "p01_s02_s01_i01.dcm")
    assert orig_dataset1.PatientName == "CompressedSamples^MR1"
    assert orig_dataset2.PatientName == "CompressedSamples^MR1"

    run_dicognito(path_to(""))

    anon_dataset1 = read_file(test_name, "p01_s01_s01_i01.dcm")
    anon_dataset2 = read_file(test_name, "a", "b", "p01_s02_s01_i01.dcm")
    assert orig_dataset1.PatientName != anon_dataset1.PatientName
    assert orig_dataset2.PatientName != anon_dataset2.PatientName


def test_non_dicom_files_ignored(capsys):
    expected_error = ""

    test_name = get_test_name()
    orig_dataset = read_original_file(test_name, "p01_s01_s01_i01.dcm")
    assert orig_dataset.PatientName == "CompressedSamples^MR1"

    run_dicognito(path_to(""))
    (actual_output, actual_error) = capsys.readouterr()

    anon_dataset = read_file(test_name, "p01_s01_s01_i01.dcm")
    assert orig_dataset.PatientName != anon_dataset.PatientName
    assert expected_error == actual_error


def test_non_dicom_files_logged_at_info(caplog):
    expected_error = "not_a_dicom_file.txt appears not to be DICOM. Skipping."

    test_name = get_test_name()
    orig_dataset = read_original_file(test_name, "p01_s01_s01_i01.dcm")
    assert orig_dataset.PatientName == "CompressedSamples^MR1"

    set_log_level(caplog, logging.INFO)
    run_dicognito("--in-place", path_to(""))
    anon_dataset = read_file(test_name, "p01_s01_s01_i01.dcm")
    assert orig_dataset.PatientName != anon_dataset.PatientName

    log_record = caplog.records[0]
    assert log_record.levelname == "INFO"
    assert log_record.getMessage().endswith(expected_error)


def test_burned_in_annotation_default(caplog):
    expected_warnings = {"Burned In Annotation is YES in " + path_to("burned_in_yes.dcm")}

    set_log_level(caplog, logging.WARNING)
    run_dicognito("--in-place", path_to(""))

    messages = {log.getMessage() for log in caplog.records if log.levelname == "WARNING"}
    assert messages == expected_warnings


def test_burned_in_annotation_unless_no(caplog):
    expected_warnings = {
        "Burned In Annotation is not specified in " + path_to("burned_in_missing.dcm"),
        "Burned In Annotation is OTHER in " + path_to("burned_in_other.dcm"),
        "Burned In Annotation is YES in " + path_to("burned_in_yes.dcm"),
    }

    set_log_level(caplog, logging.WARNING)
    run_dicognito("--in-place", path_to(""), "--assume-burned-in-annotation", "unless-no")

    messages = {log.getMessage() for log in caplog.records if log.levelname == "WARNING"}
    assert messages == expected_warnings


def test_burned_in_annotation_if_yes(caplog):
    expected_warnings = {"Burned In Annotation is YES in " + path_to("burned_in_yes.dcm")}

    set_log_level(caplog, logging.WARNING)
    run_dicognito("--in-place", path_to(""), "--assume-burned-in-annotation", "if-yes")

    messages = {log.getMessage() for log in caplog.records if log.levelname == "WARNING"}
    assert messages == expected_warnings


def test_burned_in_annotation_never(caplog):
    set_log_level(caplog, logging.WARNING)
    run_dicognito("--in-place", path_to(""), "--assume-burned-in-annotation", "never")

    messages = {log.getMessage() for log in caplog.records if log.levelname == "WARNING"}
    assert not messages


def test_burned_in_annotation_warn(caplog):
    expected_warnings = {"Burned In Annotation is YES in " + path_to("burned_in_yes.dcm")}

    set_log_level(caplog, logging.WARNING)
    run_dicognito("--in-place", path_to(""), "--on-burned-in-annotation", "warn")

    messages = {log.getMessage() for log in caplog.records if log.levelname == "WARNING"}
    assert messages == expected_warnings


def test_burned_in_annotation_fail(caplog):
    input_file_name = path_to("burned_in_yes.dcm")
    expected_message = "Burned In Annotation is YES in " + input_file_name

    with pytest.raises(SystemExit):
        run_dicognito("--in-place", path_to(""), "--on-burned-in-annotation", "fail")

    log_record = [log for log in caplog.records if log.levelname == "ERROR"][0]
    assert f"Error occurred while converting {input_file_name}. Aborting." in log_record.getMessage()
    assert expected_message in str(log_record.exc_info[1])


def test_in_place_and_output_directory_are_exclusive(capsys):
    with pytest.raises(SystemExit):
        run_dicognito(path_to(""), "--output-dir", "some_output_dir", "--in-place")

    (_, actual_error) = capsys.readouterr()
    assert "argument --in-place/-i: not allowed with argument --output-directory/-o" in actual_error


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


def test_conversion_error_logs_filename_and_error_type(caplog):
    input_file_name = path_to("bad.dcm")
    with pytest.raises(SystemExit):
        run_dicognito(input_file_name, "--output-dir", path_to("new_dir"))

    log_record = [log for log in caplog.records if log.levelname == "ERROR"][0]
    assert f"Error occurred while converting {input_file_name}. Aborting." in log_record.getMessage()
    assert log_record.exc_info is not None


def get_test_name() -> str:
    depth = 1
    while True:
        frame = sys._getframe(depth)
        if frame.f_code.co_name.startswith("test"):
            return frame.f_code.co_name
        depth += 1


def path_to(*end_of_path: str) -> str:
    return os.path.join(data_dir, get_test_name(), *end_of_path)


def run_dicognito(*extra_args: str) -> None:
    dicognito.__main__.main(("--seed", "", *extra_args))


def read_file(*directory_parts: str) -> pydicom.dataset.Dataset:
    return load_dcm(data_dir, *directory_parts)


def read_original_file(*directory_parts: str) -> pydicom.dataset.Dataset:
    return load_dcm("orig_data", *directory_parts)


def set_log_level(caplog: pytest.LogCaptureFixture, log_level: int) -> None:
    # py.test configures the logs itself, so setting the log level in the command
    # doesn't work. Instead, use caplog to set the level.
    caplog.set_level(log_level)

import os.path
import shutil
import data_for_tests
import dicognito.__main__


def test_overwrite_files(capsys):
    orig_dataset = read_file(test_overwrite_files.__name__, "orig_p01_s01_s01_i01.dcm")
    assert "CompressedSamples^MR1" == orig_dataset.PatientName

    copy_file(test_overwrite_files.__name__, "orig_p01_s01_s01_i01.dcm", "p01_s01_s01_i01.dcm")
    run_dicognito(test_overwrite_files.__name__, capsys)

    anon_dataset = read_file(test_overwrite_files.__name__, "p01_s01_s01_i01.dcm")
    assert anon_dataset.PatientName != orig_dataset.PatientName


def test_summary_mixed_files_reports_on_each_study(capsys):
    expected = """\
Accession Number Patient ID       Patient Name
---------------- ----------       ------------
821CFB2XY4A8     XRP26N7QWFM3     BYERS^YOLANDA^MYLES
0ID4RQFGHICH     YKQBAJZS5UO3     MARSHALL^BEULAH^AURELIA
NO4NP4PXEOWT     YKQBAJZS5UO3     MARSHALL^BEULAH^AURELIA
"""

    copy_file(test_summary_mixed_files_reports_on_each_study.__name__,
              "orig_p01_s01_s01_i01.dcm", "p01_s01_s01_i01.dcm")
    copy_file(test_summary_mixed_files_reports_on_each_study.__name__,
              "orig_p01_s01_s01_i02.dcm", "p01_s01_s01_i02.dcm")
    copy_file(test_summary_mixed_files_reports_on_each_study.__name__,
              "orig_p02_s01_s01_i01.dcm", "p02_s01_s01_i01.dcm")
    copy_file(test_summary_mixed_files_reports_on_each_study.__name__,
              "orig_p02_s02_s01_i01.dcm", "p02_s02_s01_i01.dcm")

    actual = run_dicognito(test_summary_mixed_files_reports_on_each_study.__name__, capsys)

    assert expected == actual


def test_summary_with_quiet_no_report(capsys):
    copy_file(test_summary_with_quiet_no_report.__name__, "orig_p01_s01_s01_i01.dcm", "p01_s01_s01_i01.dcm")
    copy_file(test_summary_with_quiet_no_report.__name__, "orig_p01_s01_s01_i02.dcm", "p01_s01_s01_i02.dcm")
    copy_file(test_summary_with_quiet_no_report.__name__, "orig_p02_s01_s01_i01.dcm", "p02_s01_s01_i01.dcm")
    copy_file(test_summary_with_quiet_no_report.__name__, "orig_p02_s01_s01_i01.dcm", "p02_s01_s01_i01.dcm")

    actual = run_dicognito(test_summary_with_quiet_no_report.__name__, capsys, "--quiet")
    expected = ""
    assert expected == actual


def run_dicognito(test_name, capsys, *extra_args):
    base_dir = os.path.dirname(__file__)
    glob = os.path.join(base_dir, "data", test_name, "p*.dcm")
    dicognito.__main__.main(("--salt", test_name, glob) + extra_args)
    (out, error) = capsys.readouterr()
    return out


def read_file(directory, name):
    return data_for_tests.load_dcm(os.path.join("data", directory, name))


def copy_file(test_name, original_name, new_name):
    base_dir = os.path.dirname(__file__)
    original_path = os.path.join(base_dir, "data", test_name, original_name)
    new_path = os.path.join(base_dir, "data", test_name, new_name)

    shutil.copyfile(original_path, new_path)

import os.path
import dicognito.__main__


def test_summary_mixed_files_reports_on_each_study(capsys):
    expected = """\
Accession Number Patient ID       Patient Name
---------------- ----------       ------------
821CFB2XY4A8     XRP26N7QWFM3     BYERS^YOLANDA^MYLES
0ID4RQFGHICH     YKQBAJZS5UO3     MARSHALL^BEULAH^AURELIA
NO4NP4PXEOWT     YKQBAJZS5UO3     MARSHALL^BEULAH^AURELIA
"""
    actual = run_dicognito(test_summary_mixed_files_reports_on_each_study.__name__, capsys)

    assert expected == actual


def run_dicognito(test_name, capsys, *extra_args):
    base_dir = os.path.dirname(__file__)
    glob = os.path.join(base_dir, "data", test_name, "p*.dcm")
    dicognito.__main__.main(("--salt", test_name, glob) + extra_args)
    (out, error) = capsys.readouterr()
    return out

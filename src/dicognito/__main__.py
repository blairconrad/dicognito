"""dicognito - anonymize DICOM files"""
from __future__ import print_function


def main(args=None):
    import sys
    import argparse
    import glob
    import os.path
    import pydicom

    from anonymizer import Anonymizer

    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Anonymize one or more DICOM files.")
    parser.add_argument("patterns", metavar="pattern", type=str, nargs="+",
                        help="the files to anonymize (may include wildcards, e.g. *.dcm)")
    parser.add_argument("--id-prefix", "-p", default="",
                        help="A short string prepended to each ID field, such as PatientID, "
                             "AccessionNumber, and so on, to make it easier to identify anonymized "
                             "studies. Longer prefixes reduce the number of available random "
                             "characters in the ID and increase the chance of collisions with other "
                             "IDs. May be combined with --id-suffix.")
    parser.add_argument("--id-suffix", "-s", default="",
                        help="A short string appended to each ID field, such as PatientID, "
                             "AccessionNumber, and so on, to make it easier to identify anonymized "
                             "studies. Longer suffixes reduce the number of available random "
                             "characters in the ID and increase the chance of collisions with other "
                             "IDs. May be combined with --id-prefix.")

    args = parser.parse_args()

    anonymizer = Anonymizer(
        id_prefix=args.id_prefix,
        id_suffix=args.id_suffix,
        )
    for pattern in args.patterns:
        for file in glob.glob(pattern):
            with pydicom.dcmread(file, force=True) as dataset:
                anonymizer.anonymize(dataset)
                (filedir, filename) = os.path.split(file)
                new_filename = os.path.join(filedir, "anon-" + filename)
                dataset.save_as(new_filename, write_like_original=False)


if __name__ == "__main__":
    main()

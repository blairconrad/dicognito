'''dicognito - anonymize DICOM files'''
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

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('patterns', metavar='pattern', type=str, nargs='+',
                        help='the files to anonymize (may include wildcards, e.g. *.dcm)')

    args = parser.parse_args()

    anonymizer = Anonymizer()
    for pattern in args.patterns:
        for file in glob.glob(pattern):
            with pydicom.dcmread(file, force=True) as dataset:
                anonymizer.anonymize(dataset)
                (filedir, filename) = os.path.split(file)
                new_filename = os.path.join(filedir, "anon-" + filename)
                dataset.save_as(new_filename, write_like_original=False)


if __name__ == "__main__":
    main()

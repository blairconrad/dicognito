'''dicognito - anonymize DICOM files'''

from __future__ import print_function

import argparse
import glob
import pydicom

from anonymizer import Anonymizer

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('patterns', metavar='pattern', type=str, nargs='+',
                    help='the files to anonymize (may include wildcards, e.g. *.dcm)')

args = parser.parse_args()

anonymizer = Anonymizer()
for pattern in args.patterns:
    for file in glob.glob(pattern):
        with pydicom.dcmread(file, force=True) as dataset:
            anonymizer.anonymize(dataset)
            dataset.save_as('out-' + file, write_like_original=False)

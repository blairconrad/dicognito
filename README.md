![Dicognito logo](https://github.com/blairconrad/dicognito/raw/main/assets/dicognito_128.png "Dicognito logo")

Dicognito is a [Python](https://www.python.org/) module and command-line utility that anonymizes
[DICOM](https://www.dicomstandard.org/) files.

Use it to anonymize one or more DICOM files belonging to one or any number of patients. Objects will remain grouped
in their original patients, studies, and series.

Anonymization causes significant attributes, such as identifiers, names, and
addresses, to be replaced by new values. Dates and times will be shifted into the
past, but their order will remain consistent within and across the files.

The package is [available on pypi](https://pypi.org/project/dicognito/) and can be installed from the command line by typing

```
pip install dicognito
```

## Anonymizing from the command line

Once installed, a `dicognito` command will be added to your Python scripts directory.
You can run it on entire filesystem trees or a collection of files specified by glob like so:

```bash
# Recurse down the filesystem, anonymizing all found DICOM files.
# Anonymized files will be placed in out-dir, named by new SOP
# instance UID.
dicognito --output-directory out-dir .

# Anonymize all files in the current directory with the dcm extension
# (-o is an alias for --output-directory).
dicognito -o out-dir *.dcm

# Anonymize all files in the current directory with the dcm extension
# but overwrite the original files.
# Note: repeatedly anonymizing the same files will cause date attributes
# to  move farther into the past.
dicognito --in-place *.dcm
```
Get more help via `dicognito --help`.

## Anonymizing from within Python

To anonymize a bunch of DICOM objects from within a Python program, import the objects using
[pydicom](https://pydicom.github.io/) and use the `Anonymizer` class:

```python
import pydicom
import dicognito.anonymizer

anonymizer = dicognito.anonymizer.Anonymizer()

for original_filename in ("original1.dcm", "original2.dcm"):
    with pydicom.dcmread(original_filename) as dataset:
        anonymizer.anonymize(dataset)
        dataset.save_as("clean-" + original_filename)
```

Use a single `Anonymizer` on datasets that might be part of the same series, or the identifiers will not be
consistent across objects.

----
Logo: Remixed from [Radiology](https://thenounproject.com/search/?q=x-ray&i=1777366)
by [priyanka](https://thenounproject.com/creativepriyanka/) and [Incognito](https://thenounproject.com/search/?q=incognito&i=7572) by [d͡ʒɛrmi Good](https://thenounproject.com/geremygood/) from [the Noun Project](https://thenounproject.com/).

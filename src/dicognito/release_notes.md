## 0.12.0

### New

- Officially support Python 3.9 ([#99](https://github.com/blairconrad/dicognito/issues/99))
- Command line flag `--version` also outputs environmental info and pydicom version ([#103](https://github.com/blairconrad/dicognito/issues/103))

### Fixed

- Unable to anonymize dataset with encapsulated pixel data that contains embedded sequence delimiter ([#96](https://github.com/blairconrad/dicognito/issues/96))


## 0.11.0

### New

- Officially support Linux (tested on Ubuntu) ([#85](https://github.com/blairconrad/dicognito/issues/85))

### Changed

- Require pydicom 2.0.0 or higher ([#92](https://github.com/blairconrad/dicognito/issues/92))

### Fixed

- Deflated files are corrupt when anonymized from the command line ([#80](https://github.com/blairconrad/dicognito/issues/80))
- Date/time offset is not always the same for a given seed ([#86](https://github.com/blairconrad/dicognito/issues/86))
- Anonymizing dataset with StationName but no Modality fails ([#97](https://github.com/blairconrad/dicognito/issues/97))


## 0.10.0

### New

- Test on Python 3.8 as well as 3.7

### Fixed

- Same patient names anonymize differently when formatted differently ([#78](https://github.com/blairconrad/dicognito/issues/78))

## 0.9.1

### Fixed

- Fails to anonymize object with Issue Date of Imaging Service Request ([#72](https://github.com/blairconrad/dicognito/issues/72))

## 0.9.0

### New

- Add option to write anonymized files to another directory ([#69](https://github.com/blairconrad/dicognito/issues/69))

## 0.8.1

### Fixed

- Fails to anonymize TimeOfLastCalibration ([#66](https://github.com/blairconrad/dicognito/issues/66))

## 0.8.0

### Changed

- Drop support for Python 2.7 ([#63](https://github.com/blairconrad/dicognito/issues/63))
- Require pydicom 1.3 or higher ([#62](https://github.com/blairconrad/dicognito/issues/62))

### New

- Anonymize placer- and filler-order numbers ([#58](https://github.com/blairconrad/dicognito/issues/58))
- Anonymize Mitra Global Patient IDs ([#60](https://github.com/blairconrad/dicognito/issues/60))

### Fixed

- Fails on multi-valued dates and times ([#61](https://github.com/blairconrad/dicognito/issues/61))

## 0.7.1

### Fixed

- Command-line anonymizer fails if an object doesn't have an AccessionNumber ([#55](https://github.com/blairconrad/dicognito/issues/55))

## 0.7.0

### Changed

- Renamed "salt" to "seed" in command-line tool and `Anonymizer` class ([#49](https://github.com/blairconrad/dicognito/issues/49))

### New

- Provide `--version` flag and `__version__` attribute ([#47](https://github.com/blairconrad/dicognito/issues/47))
- Add De-identification Method after anonymizing ([#42](https://github.com/blairconrad/dicognito/issues/42))
- Add Patient Identity Removed attribute when appropriate ([#43](https://github.com/blairconrad/dicognito/issues/43))

### Additional Items

- Add API documentation ([#45](https://github.com/blairconrad/dicognito/issues/45))
- Enforce black formatting via tests ([#50](https://github.com/blairconrad/dicognito/issues/50))
- Enforce PEP-8 naming conventions via tests ([#53](https://github.com/blairconrad/dicognito/issues/53))

## 0.6.0

### Changed

- Made InstitutionName more unique ([#19](https://github.com/blairconrad/dicognito/issues/19))

### Additional Items

- Add how_to_build.md ([#8](https://github.com/blairconrad/dicognito/issues/8))
- Update CONTRIBUTING.md ([#9](https://github.com/blairconrad/dicognito/issues/9))
- Update package keywords and pointer to releases ([#37](https://github.com/blairconrad/dicognito/issues/37))
- Update docs in README ([#36](https://github.com/blairconrad/dicognito/issues/36))

## 0.5.0

### New

- Add option to anonymize directory trees ([#22](https://github.com/blairconrad/dicognito/issues/22))
- Support python 3.7 ([#31](https://github.com/blairconrad/dicognito/issues/31))

### Additional Items

- Format code using [black](https://black.readthedocs.io/en/stable/)
  ([#33](https://github.com/blairconrad/dicognito/issues/33))

## 0.4.0

### Changed
- Anonymize files in place ([#21](https://github.com/blairconrad/dicognito/issues/21))

### New

- Print summary of anonymized studies ([#2](https://github.com/blairconrad/dicognito/issues/2))

### Additional Items

- Use tox for testing ([#28](https://github.com/blairconrad/dicognito/issues/28))

## 0.3.1.post7

### Fixed

- Cannot anonymize instance lacking `PatientSex` ([#24](https://github.com/blairconrad/dicognito/issues/24))

### Additional Items

- Test on a CI environment ([#11](https://github.com/blairconrad/dicognito/issues/11))
- Add tools for preparing release branch and auto-deploying ([#17](https://github.com/blairconrad/dicognito/issues/17))

## 0.3.0

### New
- Add option to add a prefix or suffix for some IDs ([#1](https://github.com/blairconrad/dicognito/issues/1))


## 0.2.1

### New
- Initial release, with minimal functionality

### With special thanks for contributions to this release from:
- [Paul Duncan](https://github.com/paulsbduncan)

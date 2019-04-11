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

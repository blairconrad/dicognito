import setuptools

package_name = "dicognito"
url = "https://github.com/blairconrad/dicognito"

with open("src/dicognito/release_notes.md") as notes:
    for line in notes:
        if line.startswith("## "):
            version = line[3:].strip()
            break

with open("README.md") as fh:
    long_description = fh.read()

setuptools.setup(
    name=package_name,
    version=version,
    author="Blair Conrad",
    author_email="blair@blairconrad.com",
    description="A tool for anonymizing DICOM files",
    keywords="anonymize deidentify dicom python",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    download_url="{url}/releases/{version}".format(**vars()),
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Healthcare Industry",
    ],
    install_requires=["pydicom >= 2.3.1, < 3.0.0"],  # sync with tox.ini
    entry_points={"console_scripts": ["dicognito=dicognito.__main__:main"]},
)

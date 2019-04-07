import setuptools

package_name = "dicognito"
url = "https://github.com/blairconrad/dicognito"

with open("src/dicognito/release_notes.md", "r") as notes:
    for line in notes:
        if line.startswith("## "):
            version = line[3:].strip()
            break

with open("README.md", "r") as fh:
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
    download_url="%(url)s/releases/%(version)s" % vars(),
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Healthcare Industry",
    ],
    install_requires=["pydicom"],
    entry_points={"console_scripts": ["dicognito=dicognito.__main__:main"]},
)

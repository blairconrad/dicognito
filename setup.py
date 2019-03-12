import setuptools

version = "0.2.1"
package_name = "dicognito"
url = "https://github.com/blairconrad/dicognito"

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=package_name,
    version=version,
    author="Blair Conrad",
    author_email="blair@blairconrad.com",
    description="A tool for anonymizing DICOM files",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    download_url="%(url)s/archive/%(version)s.tar.gz" % vars(),
    packages=[package_name],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Healthcare Industry",
    ],
    install_requires=[
        "pydicom",
    ],
    entry_points={
        "console_scripts": ["dicognito=dicognito.__main__:main"],
    }
)

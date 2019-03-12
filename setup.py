import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dicognito",
    version="0.1.4",
    author="Blair Conrad",
    author_email="blair@blairconrad.com",
    description="A tool for anonymizing DICOM files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/blairconrad/dicognito",
    packages=["dicognito"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Healthcare Industry",
    ],
    install_requires=[
        'pydicom',
    ],
    entry_points={
        'console_scripts': ['dicognito=dicognito.__main__:main'],
    }
)

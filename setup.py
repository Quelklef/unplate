import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name                          = "unplate",
    version                       = "0.1.0",
    author                        = "Quelklef",
    author_email                  = "",
    description                   = "A templating language embedded into Python",
    long_description              = long_description,
    long_description_content_type = "text/markdown",
    url                           = "https://github.com/quelklef/unplate",
    packages                      = setuptools.find_packages(),
    classifiers                   = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires               = '>=3.6',
)

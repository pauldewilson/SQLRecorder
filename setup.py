import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sqlrecorder",
    version="1.0",
    author="Paul Wilson",
    author_email="pauldewilson@gmail.com",
    description="Python Wrapper for use in recording the success or failure of any functions to a SQL table, along with any respective arguments or keyword arguments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pauldewilson/SQLRecorder",
    project_urls={
        "Bug Tracker": "https://github.com/pauldewilson/SQLRecorder/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
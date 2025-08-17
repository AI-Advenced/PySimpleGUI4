from setuptools import setup

import PySimpleGUI4 as sg

with open("README.md", "rb") as f:
    long_description = f.read().decode("utf-8")

keywords = ["PySimpleGui", "fork", "GUI", "UI", "tkinter"]

setup(
    name="PySimpleGUI4",
    version=sg.__version__,
    description="The free-forever and simple Python GUI framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=sg.__author__,
    author_email=sg.__email__,
    keywords=keywords,
    url="https://github.com/yunluo/PySimpleGUI4",
    license=sg.__license__,
    platforms=["all"],
    python_requires=">=3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics",
        "Operating System :: OS Independent",
    ],
    requires=["pyguievent"],
    py_modules=["PySimpleGUI4"],
    project_urls={
        "Source": "https://github.com/yunluo/PySimpleGUI4",
    },
)

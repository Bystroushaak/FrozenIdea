#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from setuptools import setup


# Variables ===================================================================
changelog = open('CHANGELOG.rst').read()
long_description = "\n\n".join([
    open('README.rst').read(),
    changelog
])


# Functions ===================================================================
def getVersion(data):
    """
    Parse version from changelog written in RST format.
    """
    def allSame(s):
        return not any(filter(lambda x: x != s[0], s))

    def hasDigit(s):
        return any(char.isdigit() for char in s)

    data = data.splitlines()
    return next((
        v
        for v, u in zip(data, data[1:])  # v = version, u = underline
        if len(v) == len(u) and allSame(u) and hasDigit(v) and "." in v
    ))


# Actual setup definition =====================================================
setup(
    name='FrozenIdea',
    version=getVersion(changelog),
    description="Simple IRC class skelet for quick bot creation.",
    long_description=long_description,
    url='https://github.com/Bystroushaak/FrozenIdea',

    author='Bystroushaak',
    author_email='bystrousak@kitakitsune.org',

    classifiers=[
        "Development Status :: 4 - Beta",
        'Intended Audience :: Developers',

        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",

        "License :: OSI Approved :: MIT License",

        "Topic :: Communications",
    ],
    license='MIT',

    py_modules=['frozenidea'],

    zip_safe=False,
    include_package_data=True,
)

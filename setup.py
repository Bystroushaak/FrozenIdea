#! /usr/bin/env python
from setuptools import setup
from setuptools import find_packages


changelog = open('CHANGELOG.rst').read()
long_description = "\n\n".join([
    open('README.rst').read(),
    changelog
])


def get_version(data):
    """
    Parse version from changelog written in RST format.
    """
    def all_same(s):
        return not any(filter(lambda x: x != s[0], s))

    def has_digit(s):
        return any(char.isdigit() for char in s)

    data = data.splitlines()
    return next((
        v
        for v, u in zip(data, data[1:])  # v = version, u = underline
        if len(v) == len(u) and all_same(u) and has_digit(v) and "." in v
    ))


setup(
    name='FrozenIdea',
    version=get_version(changelog),
    description="IRC bot toolkit.",
    long_description=long_description,
    url='https://github.com/Bystroushaak/FrozenIdea',

    author='Bystroushaak',
    author_email='bystrousak@kitakitsune.org',

    classifiers=[
        "Development Status :: 4 - Beta",
        'Intended Audience :: Developers',

        "Programming Language :: Python",
        "Programming Language :: Python :: 3",

        "License :: OSI Approved :: MIT License",

        "Topic :: Communications",
    ],
    license='MIT',

    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=True,
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# author:        alisue
# date:            2011/03/22
#
from setuptools import setup, find_packages

version = "0.1.6"

def read(filename):
    import os.path
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name="django-universaltag",
    version=version,
    description = "Universal tagging library for Django",
    long_description=read('README.rst'),
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords = "django tagging universal tag",
    author = "Alisue",
    author_email = "lambdalisue@hashnote.net",
    url=r"https://github.com/lambdalisue/django-universaltag",
    download_url = r"https://github.com/lambdalisue/django-universaltag/tarball/master",
    license = 'MIT',
    packages = find_packages(exclude=['tests']),
    include_package_data = True,
    zip_safe=False,
    install_requires=[
        'distribute',
        'setuptools-git',
        'django>=1.2',
        'django-piston>=0.2.2',
    ],
    tests_require = [
    ],
    test_suite = 'runtests.runtests',
)


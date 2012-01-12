#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# author:        alisue
# date:            2011/03/22
#
from setuptools import setup, find_packages

version = "0.1rc3"

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
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords = "django tagging universal tag",
    author = "Alisue",
    author_email = "lambdalisue@hashnote.net",
    url=r"https://github.com/lambdalisue/django-universaltag",
    download_url = r"https://github.com/lambdalisue/django-universaltag/tarball/master",
    license = 'BSD',
    packages = find_packages(),
    include_package_data = True,
    install_requires=[
        'setuptools',
        'setuptools-git',
        'django>=1.2',
        'django-piston>=0.2.2',
    ],
)


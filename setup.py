#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

f = open('README.md')
long_description = f.read().strip()
f.close()

# Ridiculous as it may seem, we need to import multiprocessing and
# logging here in order to get tests to pass smoothly on python 2.7.
try:
    import multiprocessing
    import logging
except ImportError: 
    pass

setup(
    name='quilt',
    version='0.0.1',
    description="A distributed chat lcient intended for the Sugar environment",
    long_description=long_description,
    author='Ross Delinger',
    author_email='posiden@helixoide.com',
    url='http://github.com/FOSSRIT/quilt/',
    license='MIT',
    classifiers=[
        "License :: OSI Approved :: MIT",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
    ],
    install_requires=['pyzmq-static',
    ],
    tests_require=[
        'nose',
    ],
    test_suite='nose.collector',
    packages=['quilt'],
    include_package_data=True,
    zip_safe=False,
    entry_points="""
    [console_scripts]
    quilt-console = quilt:test_console
    """
)

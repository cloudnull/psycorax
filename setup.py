#!/usr/bin/env python

import setuptools
import sys
import os
import tarfile
import time
import subprocess

# Local Packages
import psycorax.info

if sys.version_info < (2, 6, 0):
    sys.stderr.write("PsycoRAX Presently requires Python 2.6.0 or greater\n")
    sys.exit('Upgrade python because your version of it is VERY deprecated\n')

#with open('README') as file:
long_description = 'Things and Stuff'

T_M = ['paramiko',
      'Fabric',
      'python-daemon',
      'argparse',
      'bookofnova']

setuptools.setup(
    name=psycorax.info.__appname__,
    version=psycorax.info.__version__,
    author=psycorax.info.__author__,
    author_email=psycorax.info.__email__,
    description='Stress Testing and Pain Creator',
    long_description='Here is a long description',
    license=psycorax.info.__license__,
    packages=['psycorax','psycorax.attacks'],
    url=psycorax.info.__url__,
    install_requires=T_M,
    classifiers=[
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    entry_points={
        "console_scripts":
            ["psycorax = psycorax.executable:run_psycorax"]
    }
)
#!/usr/bin/env python
import setuptools
import sys
import os
import tarfile
import time

# Local Packages
from psycorax import info, strings

if sys.version_info < (2, 6, 0):
    sys.stderr.write("PsycoRAX Presently requires Python 2.6.0 or greater\n")
    sys.exit('Upgrade python because your version of it is VERY deprecated\n')

#with open('README') as file:
long_description = 'Things and Stuff'

T_M = ['paramiko',
       'Fabric',
       'python-daemon',
       'argparse',
       'bookofnova',
       'prettytable']

setuptools.setup(
    name=info.__appname__,
    version=info.__version__,
    author=info.__author__,
    author_email=info.__email__,
    description='Stress Testing and Pain Creator',
    long_description='Here is a long description',
    license=info.__license__,
    packages=['psycorax', 'psycorax.attacks'],
    url=info.__url__,
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


def config_files_setup():
    """
    setup will copy the config file in place.
    """
    print('Moving the the System Config file in place')
    name = 'config.cfg'
    path = '/etc/%s' % info.__appname__
    full = '%s%s%s' % (path, os.sep, name)
    conf_file = strings.config_file % {'full_path': full}
    if not os.path.isdir(path):
        os.mkdir(path)
        with open(full, 'w+') as conf_f:
            conf_f.write(conf_file)
    else:
        if not os.path.isfile(full):
            with open(full, 'w+') as conf_f:
                conf_f.write(conf_file)
        else:
            print('Their was a configuration file found, I am compressing the '
                  'old version and will place the new one on the system.')
            not_time = time.time()
            backupfile = '%s.%s.backup.tgz' % (full, not_time)
            tar = tarfile.open(backupfile, 'w:gz')
            tar.add(full)
            tar.close()
            with open(full, 'w+') as conf_f:
                conf_f.write(conf_file)
    if os.path.isfile(full):
        os.chmod(full, 0600)
    print('Configuration file is ready.  Please set your credentials in : %s'
          % full)


if len(sys.argv) > 1:
    if sys.argv[1] == 'install':
        # Run addtional Setup things
        config_files_setup()

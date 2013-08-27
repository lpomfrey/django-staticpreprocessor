#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
from setuptools import setup, find_packages


def get_version(package):
    '''
    Return package version as listed in `__version__` in `init.py`.
    '''
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search(
        '^__version__ = [\'"]([^\'"]+)[\'"]', init_py, re.MULTILINE
    ).group(1)


version = get_version('staticpreprocessor')


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    args = {'version': version}
    print('You probably want to also tag the version now:')
    print(' git tag -a release/{version} -m \'version {version}\''.format(
        **args))
    print(' git push --tags')
    sys.exit()


setup(
    name='django-staticpreprocessor',
    version=version,
    url='http://github.com/lpomfrey/django-staticpreprocessor',
    license='BSD',
    description='Pre-process static files in Django',
    author='Luke Pomfrey',
    author_email='lpomfrey@gmail.com',
    packages=find_packages(exclude=['test_project', 'test_app']),
    install_requires=open('requirements.txt').read().split('\n'),
    tests_require=['mock'],
    test_suite='runtests.runtests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP'
    ]
)

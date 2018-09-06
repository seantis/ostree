# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

name = 'ostree'
description = (
    'Pulls containers and turns them into OS trees for systemd-nspawn.'
)
version = '0.1.0'


def get_long_description():
    readme = open('README.md').read()
    history = open('HISTORY.md').read()

    # cut the part before the description to avoid repetition on pypi
    readme = readme[readme.index(description) + len(description):]

    return '\n'.join((readme, history))


setup(
    name=name,
    version=version,
    description=description,
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='http://github.com/seantis/ostree',
    author='Seantis GmbH',
    author_email='info@seantis.ch',
    license='MIT',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=name.split('.')[:-1],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'cached_property',
        'click',
        'google-auth',
        'requests',
    ],
    extras_require=dict(
        test=[
            'coverage',
            'flake8',
            'pytest',
        ],
    ),
    entry_points={
        'console_scripts': 'ostree=ostree.cli:cli'
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ]
)

# -*- coding: utf-8 -*-

'''
setup

All rights reserved for niceStudio.
'''
import os
import sys

src_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'src')

sys.path.insert(0, src_path)

import nicedjango

version = nicedjango.__version__

django_extra_packages = []


from setuptools import setup, find_packages

setup(
    name='nicedjango',
    version=version,
    description="",
    long_description='''\
''',
    author='cdchen',
    author_email='cdchen@nicestudio.com.tw',
    url='http://projects.nicestudio.com.tw/passpass_websuite',
    license='',
    packages=find_packages('src', exclude=['docs', 'tests']),
    package_dir={
        '': 'src'
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        'django',
        'django-uuidfield',
    ] + django_extra_packages,
    setup_requires=[
        'sphinx',
    ],
    entry_points="""
    """,
)


# End of file

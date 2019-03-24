# -*- coding: utf8 -*-
from __future__ import absolute_import
from setuptools import setup
import pathlib as pa
import codecs as cd

package_version = '0.9.13'
package_name    = 'PyLUCCBA'

with pa.Path('requirements.txt').open() as requirements:
    requires = [l.strip() for l in requirements]

with cd.open('README.md', encoding='utf-8') as readme_f:
    readme = readme_f.read()

setup(
    license      = 'MIT',
    name         = package_name,
    version      = package_version,
    packages     = [package_name],
    package_data = {
        package_name: [
            'examples/*',
            'examples/*/*',
            'resources/*',
            'resources/*/*',
            'resources/*/*/*',
        ]
    },
    description =(
        "A Land-Use-Change Cost-Benefit-Analysis "
        "calculator coded in Python27&3, %s."%package_name
    ),
    long_description              = readme,
    long_description_content_type = 'text/markdown',
    author       = 'Laurent Faucheux',
    author_email = "laurent.faucheux@hotmail.fr",
    url          = 'https://github.com/lfaucheux/%s'%package_name,
    download_url = 'https://github.com/lfaucheux/{}/archive/{}.tar.gz'.format(package_name, package_version),
    classifiers  = [
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
    ],
    keywords = [
        'land use change',
        'cost benefit analysis',
        'environmental economics'
    ],
    install_requires = requires,
)

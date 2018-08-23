#from distutils.core import setup
from setuptools import setup
from PyLUCCBA import __version__ as v

setup(
    name='PyLUCCBA',
    packages=['PyLUCCBA'],
    package_data={
        'PyLUCCBA': [
            'examples/*',
            'resources/*',
            'resources/*/*',
            'resources/*/*/*',
        ]
    },
    version=v,
    description="A Land-Use-Change Cost-Benefit-Analysis calculator coded in Python2&3, PyLUCCBA.",
    author='Laurent Faucheux',
    author_email="laurent.faucheux@hotmail.fr",
    url='https://github.com/lfaucheux/PyLUCCBA',
    download_url = 'https://github.com/lfaucheux/PyLUCCBA/archive/{}.tar.gz'.format(v),
    keywords = ['land use change', 'cost benefit analysis', 'environmental economics'],
    classifiers=[
        'Programming Language :: Python'
    ],
    install_requires=[
        'numpy>=1.14.0',
        'scipy>=1.0.0',
        'openpyxl>=2.2.2',
        'matplotlib>=1.4.3'
    ]
)

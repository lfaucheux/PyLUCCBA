from distutils.core import setup
from PyLUCCBA import __version__ as v

setup(
    name='PyLUCCBA',
    packages=['PyLUCCBA'],
    package_data={
        'PyLUCCBA': [
            'examples/*',
            'resources/*',
        ]
    },
    version=v,
    description="A Land-Use-Change Cost-Benefit-Analysis calculator coded in Python, PyLUCCBA.",
    author='Laurent Faucheux',
    author_email="laurent.faucheux@hotmail.fr",
    url='https://github.com/lfaucheux/PyLUCCBA',
    download_url = 'https://github.com/lfaucheux/PyLUCCBA/archive/{}.tar.gz'.format(v),
    keywords = ['land use change', 'cost benefit analysis', 'environmental economics'],
    classifiers=[],
)

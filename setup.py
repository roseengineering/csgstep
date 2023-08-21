
import re
from distutils.core import setup

with open('csgstep/csgstep.py') as f:
    for ln in f:
        m = re.search("__version__ = '(\S+)'", ln)
        if m: __version__ = m.group(1)

setup(
    name='csgstep',
    version=__version__,
    packages=['csgstep'],
    package_dir={'csgstep': 'csgstep'},
    install_requires=[ 'numpy' ]
)



from distutils.core import setup

exec(open('csgstep/csgstep.py').read())

setup(
    name='csgstep',
    version=__version__,
    packages=['csgstep'],
    package_dir={'csgstep': 'csgstep'},
    install_requires=[ 'numpy' ]
)


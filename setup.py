from setuptools import setup, find_packages
from os import path, environ

cur_dir = path.abspath(path.dirname(__file__))

with open(path.join(cur_dir, 'requirements.txt'), 'r') as f:
    requirements = f.read().split()



setup(
    name='lcls-cu-acc-live',
    version = 'v0.1.1',
    packages=find_packages(),  
    package_dir={'lcls_cu_acc_live':'lcls_cu_acc_live'},
    author='Jacqueline Garrahan',
    author_email='jgarra@slac.stanford.edu',  
    url='https://github.com/slaclab/lcls-live',
    description='Live Bmad model of copper beamlines.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=requirements,
    include_package_data=True,
    python_requires='>=3.7',
    entry_points={
    'console_scripts': [
        'start-server=lcls_cu_acc_live.server:main',
        'start-bridge=lcls_cu_acc_live.bridge:main'],
    },
)

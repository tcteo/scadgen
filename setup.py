from setuptools import setup, find_packages

setup(
    name='scadgen',
    version='0.0.1',
    author='TC Teo',
    description='A library for generating OpenSCAD models with Python.',
    packages=find_packages(where='./src'),
    package_dir={
        '': 'src'
    },
    install_requires=[],
    include_package_data=True,
)

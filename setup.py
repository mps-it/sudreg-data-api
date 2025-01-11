from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='SudskiRegistarDataAPI',
    version='0.0.1',
    url='https://github.com/mps-it/sudreg-data-api',
    author='MPS IT',
    author_email='info@mps-it.hr',
    description='Package for accessing data from the Sudreg API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    keywords='Sudski Registar, Sudski Registar API'
)
"""
A setuptools based setup module.
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import setuptools
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='tkshapes',
    version='0.0.3',
    description='Draw and interact with shapes on the Tkinter canvas',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bentlema/tkshapes',
    author='Mark Bentley',
    author_email='bentlema@yahoo.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='tkinter',
    packages=setuptools.find_packages(where="src", exclude=['contrib', 'docs', 'tests']),
    package_dir={"": "src"},
    project_urls={
        'Bug Reports': 'https://github.com/bentlema/tkshapes/issues',
        'Source': 'https://github.com/bentlema/tkshapes/',
    },
)

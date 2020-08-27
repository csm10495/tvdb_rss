from setuptools import setup
import os
import sys

setup(
    name='tvdb_rss',
    author='csm10495',
    author_email='csm10495@gmail.com',
    url='https://github.com/csm10495/tvdb_rss',
    version='0.0.12',
    packages=['tvdb_rss'],
    license='MIT License',
    python_requires='>=3.7',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    include_package_data = True,
    install_requires=['csmlog', 'requests', 'feedgen'],
)
import io
import os
import sys
from glob import glob
from distutils.command.sdist import sdist
from setuptools import setup, Extension


module1 = Extension('msgpackfinder',
                    sources = ['msgpackstream/findformat.c'])


setup(
  name = 'msgpackstream',
  packages = ['msgpackstream'], # this must be the same as the name above
  version = '1.0.9',
  description = 'A SAX-like MessagegPack library in python to deserialize messages from an input stream',
  author = 'Salim Malakouti',
  author_email = 'salim.malakouti@gmail.com',
  license = 'MIT',
  url = 'https://github.com/salimm/msgpack-pystream', # use the URL to the github repo
  download_url = 'http://github.com/salimm/msgpack-pystream/archive/1.0.9.tar.gz', # I'll explain this in a second
  keywords = ['python','msgpack','serialization','binary','fast'], # arbitrary keywords
  classifiers = ['Programming Language :: Python'],
  install_requires=['msgpack','enum34'],
  ext_modules = [module1]
)

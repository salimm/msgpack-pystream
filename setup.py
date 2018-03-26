# import io
# import os
# import sys
# from glob import glob
# from distutils.command.sdist import sdist
from setuptools import setup, Extension, find_packages


module1 = Extension('mpstream_cunpacker',
                    sources = [
                               'msgpackpyc/src/unpacker.cpp',
                               'msgpackpyc/src/unpackerapi.cpp',
                               'msgpackpyc/src/ParserInfo.cpp',                               
                               'msgpackpyc/src/Event.cpp',
                               'msgpackpyc/src/ExtType.cpp',
                               'msgpackpyc/src/HeaderUtil.cpp',
                               'msgpackpyc/src/ParserState.cpp',
                               ],
#                     libraries=['libs/'],
                    include_dirs=['msgpackpyc/include/'],
                    language = "c++"
                     
                    )



setup(
  name = 'msgpackstream',
  packages = ['msgpackstream','msgpackstream.backend', 'msgpackstream.backend.python','msgpackstream.backend.pyc'], # this must be the same as the name above
  version = '1.2.7',
  description = 'A SAX-like MessagegPack library in python to deserialize messages from an input stream',
  author = 'Salim Malakouti',
  author_email = 'salim.malakouti@gmail.com',
  license = 'MIT',
  url = 'https://github.com/salimm/msgpack-pystream', # use the URL to the github repo
  download_url = 'http://github.com/salimm/msgpack-pystream/archive/1.2.7.tar.gz', # I'll explain this in a second
  keywords = ['python','msgpack','serialization','binary','fast'], # arbitrary keywords
  classifiers = ['Programming Language :: Python'],
  install_requires=['msgpack_python','msgpack','enum34'],
  ext_modules = [module1]
)

'''
Created on Feb 5, 2018

@author: Salim
'''
import msgpack
from msgpackstream.backend.pyc.stream import unpack as unpackc
from msgpackstream.backend.python.stream import unpack as unpackp
from ddt import data,ddt
import unittest
from _io import BytesIO

@ddt
class TestSingleByteTypes(unittest.TestCase):

    @data(unpackc, unpackp)
    def test_nested1(self,f):
        bdata = msgpack.packb([{"f1":1}, {"x":2, 3:b's', "t":{"xx":5}, "yy":99, "o2":{}}])
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        for e in events:
            print(e)
    
    
    def create_instream(self, bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff
    
if __name__ == '__main__':
    unittest.main()

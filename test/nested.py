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
    
    @data(unpackc, unpackp)
    def test_nested_arrays(self,f):
        
        bdata = msgpack.packb([[1,2,3,4]]*4)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        
        self.assertEquals(26,len(events))
        
    @data(unpackc, unpackp)
    def test_nested_arrays_in_map(self,f):
        
        bdata = msgpack.packb({"x":[[1,2,3,4]]*4})
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        
        self.assertEquals(29,len(events))
        
    @data(unpackc, unpackp)
    def test_nested_myulti_arrays_in_map(self,f):
        
        bdata = msgpack.packb({"x":[[1,2,3,4]]*4, "y":[{1:2}]*10})
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        
        self.assertEquals(29+43,len(events))
        
    @data(unpackc, unpackp)
    def test_nested_myulti_arrays_in_map_in_array(self,f):
        
        bdata = msgpack.packb([{"x":[[1,2,3,4]]*4, "y":[{1:2}]*10}]*2)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        
        self.assertEquals((29+43)*2+2,len(events))
    
    def create_instream(self, bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff
    
if __name__ == '__main__':
    unittest.main()

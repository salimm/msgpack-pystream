'''
Created on Feb 5, 2018

@author: Salim
'''
import msgpack
from msgpackstream.format import EventType
from msgpackstream.stream import unpack
import unittest
from _io import BytesIO


class TestSingleByteTypes(unittest.TestCase):

    def test_nested1(self):
        bdata = msgpack.packb([{"f1":1}, {"x":2, 3:b's', "t":{"xx":5}, "yy":99, "o2":{}}])
        buff = self.create_instream(bdata)
        events = [e for e in unpack(buff)]
        for e in events:
            print(e)
    
    
    def create_instream(self, bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff
    
if __name__ == '__main__':
    unittest.main()

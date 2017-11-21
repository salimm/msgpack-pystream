'''
Created on Nov 20, 2017

@author: Salim
'''
import unittest
import msgpack
from _io import BytesIO
import msgpackstream




class TestSingleByteTypes(unittest.TestCase):

    def test_nil(self):
        bdata = msgpack.packb(None)
        buff = self.create_instream(bdata)
        events = [e for e in msgpackstream.stream_unpack(buff)]
        self.assertEqual(1, len(events))
        

    def test_isupper(self):
        pass

    def test_split(self):
        pass
    
    def create_instream(self,bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff
    
    
if __name__ == '__main__':
    unittest.main()
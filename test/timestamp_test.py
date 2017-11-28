'''
Created on Nov 21, 2017

@author: Salim
'''
import unittest
from _io import BytesIO
import msgpackstream.stream as msgpackapi
from msgpackstream.format import FormatType, ExtType
from msgpackstream.stream import  EventType, ExtTypeParser
import datetime


    
class TestExtFormats(unittest.TestCase):
    
    
        
    def test_timestamp_ext4(self):
        buff = self.create_instream(b'\xd6\xff\x5A\x1D\x69\x7E')
        events = [e for e in msgpackapi.unpack(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_4,-1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(datetime.datetime.fromtimestamp(1511876990), events[0][3])
    
    
    def test_timestamp_ext8_no_ns(self):
        buff = self.create_instream(b'\xd7\xff\x00\x00\x00\x00\x5A\x1D\x69\x7E')
        events = [e for e in msgpackapi.unpack(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_8,-1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(datetime.datetime.fromtimestamp(1511876990), events[0][3])
        
        
    def test_timestamp_ext8_with_ns(self):
        buff = self.create_instream(b'\xd7\xff\xEE\x6B\x28\x00\x5A\x1D\x69\x7E') # plus 10s in nanoseconds
        events = [e for e in msgpackapi.unpack(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_8,-1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(datetime.datetime.fromtimestamp(1511876990+1), events[0][3]) # plus  1s
        
    def test_timestamp_12_no_ns(self):
        buff = self.create_instream(b'\xc7\x0C\xff\x00\x00\x00\x00\x00\x00\x00\x00\x5A\x1D\x69\x7E') # plus 1s in nanoseconds
        events = [e for e in msgpackapi.unpack(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_8,-1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(datetime.datetime.fromtimestamp(1511876990), events[0][3]) # plus  1s
        
        
    def test_timestamp_12_with_ns(self):
        buff = self.create_instream(b'\xc7\x0C\xff\x3B\x9A\xCA\x00\x00\x00\x00\x00\x5A\x1D\x69\x7E') # plus 1s in nanoseconds
        events = [e for e in msgpackapi.unpack(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_8,-1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(datetime.datetime.fromtimestamp(1511876990+1), events[0][3]) # plus  1s

   

    def create_instream(self, bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff    
    
    
if __name__ == '__main__':
    unittest.main()
    
    

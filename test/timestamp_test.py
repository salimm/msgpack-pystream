'''
Created on Nov 21, 2017

@author: Salim
'''
import unittest
from _io import BytesIO
from  msgpackstream.backend.python.stream import unpack as unpackp
from  msgpackstream.backend.pyc.stream import unpack as unpackc
from ddt import data,ddt
from msgpackstream.defs import FormatType, ExtType
from msgpackstream.defs import EventType
import datetime


    
@ddt
class TestExtFormats(unittest.TestCase):
    
        
    @data( unpackc, unpackp)
    def test_timestamp_ext4(self,f):
        buff = self.create_instream(b'\xd6\xff\x5A\x1D\x69\x7E')
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_4.value.code,-1), events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(datetime.datetime.fromtimestamp(1511876990), events[0][2])
    
    
    @data( unpackc, unpackp)
    def test_timestamp_ext8_no_ns(self,f):
        buff = self.create_instream(b'\xd7\xff\x00\x00\x00\x00\x5A\x1D\x69\x7E')
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_8.value.code,-1), events[0][1]) # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        print(datetime.datetime.fromtimestamp(1511876990))
        self.assertEqual(datetime.datetime.fromtimestamp(1511876990), events[0][2])
        
    
    @data( unpackc, unpackp)
    def test_timestamp_ext8_with_ns(self,f):
        buff = self.create_instream(b'\xd7\xff\xEE\x6B\x28\x00\x5A\x1D\x69\x7E') # plus 10s in nanoseconds
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_8.value.code,-1), events[0][1]) # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(datetime.datetime.fromtimestamp(1511876990+1), events[0][2]) # plus  1s
#       
    @data( unpackc, unpackp)
    def test_timestamp_12_no_ns(self,f):
        buff = self.create_instream(b'\xc7\x0C\xff\x00\x00\x00\x00\x00\x00\x00\x00\x5A\x1D\x69\x7E') # plus 1s in nanoseconds
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        print(events[0][1])
        self.assertEqual(ExtType(FormatType.EXT_8.value.code,-1), events[0][1]) # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(datetime.datetime.fromtimestamp(1511876990), events[0][2]) # plus  1s
         
    @data( unpackp,unpackc)
    def test_timestamp_12_with_ns(self,f):
        buff = self.create_instream(b'\xc7\x0C\xff\x3B\x9A\xCA\x00\x00\x00\x00\x00\x5A\x1D\x69\x7E') # plus 1s in nanoseconds
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_8.value.code,-1), events[0][1]) # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(datetime.datetime.fromtimestamp(1511876990+1), events[0][2]) # plus  1s

   

    def create_instream(self, bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff    
    
    
if __name__ == '__main__':
    unittest.main()
    
    

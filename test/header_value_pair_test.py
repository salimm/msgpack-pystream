'''
Created on Nov 20, 2017

@author: Salim
'''

import unittest
import msgpack
from _io import BytesIO
from msgpackstream.defs import FormatType
from msgpackstream.backend.pyc.stream import unpack as unpackc
from msgpackstream.backend.python.stream import unpack as unpackp
from ddt import data,ddt
from msgpackstream.defs import EventType


@ddt
class HeaderValuePairTest(unittest.TestCase):

    @data(unpackc, unpackp)
    def test_float64(self,f):
        bdata = msgpack.packb(112321312.12312321312312)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.FLOAT_64.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(112321312.12312321312312, events[0][2])
    
    
    @data(unpackc, unpackp)
    def test_unint8(self,f):
        bdata = msgpack.packb(150)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.UINT_8.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(150, events[0][2])
        
    @data(unpackc, unpackp)
    def test_unint16(self,f):
        bdata = msgpack.packb(1211)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.UINT_16.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(1211, events[0][2])
        
    
    @data(unpackc, unpackp)
    def test_unint32(self,f):
        bdata = msgpack.packb(1211123)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.UINT_32.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(1211123, events[0][2])
    
    @data(unpackc, unpackp)
    def test_unint64(self,f):
        bdata = msgpack.packb(12121234561111)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.UINT_64.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(12121234561111, events[0][2])
        
    @data(unpackc, unpackp)   
    def test_int8(self,f):
        buff = self.create_instream(b'\xD0\x01')
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.INT_8.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(1, events[0][2])
        
        bdata = msgpack.packb(-50)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.INT_8.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(-50, events[0][2])
        
    @data(unpackc, unpackp)
    def test_int16(self,f):
        buff = self.create_instream(b'\xD1\x00\x01')
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.INT_16.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(1, events[0][2])
        
        bdata = msgpack.packb(-1124)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.INT_16.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual( events[0][2],-1124)
        
        
    @data(unpackc, unpackp)
    def test_int32(self,f):
        buff = self.create_instream(b'\xD2\x00\x00\x00\x01')
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.INT_32.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(events[0][2],1)
        
        bdata = msgpack.packb(-11234213)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.INT_32.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual( events[0][2],-11234213)
        
    @data(unpackc, unpackp)
    def test_int64(self,f):
        buff = self.create_instream(b'\xD3\x00\x00\x00\x00\x00\x00\x00\x01')
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.INT_64.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual( events[0][2],1)
        
        bdata = msgpack.packb(-1243546578691)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.INT_64.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual( events[0][2],-1243546578691)
        
    

   
    def create_instream(self,bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff
    
    
if __name__ == '__main__':
    unittest.main()
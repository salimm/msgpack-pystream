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
class HeaderWithLengthValueTest(unittest.TestCase):

    @data(unpackc, unpackp)
    def test_fixst_empty(self,f):
        events = [e for e in f(self.create_instream(b'\xA0'))]
        self.assertEqual( 1, len(events))
        self.assertEqual(FormatType.FIXSTR.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual('', events[0][2])

    @data(unpackc, unpackp)
    def test_fixstr(self,f):
        bdata = msgpack.packb('test string')
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.FIXSTR.value.code, events[0][1]) # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual('test string', events[0][2])
        
    @data(unpackc, unpackp)
    def test_fixarrray_empty(self,f):
        events = [e for e in f(self.create_instream(b'\x90'))]
        self.assertEqual( 2, len(events))
        self.assertEqual(FormatType.FIXARRAY.value.code, events[0][1]) # @UndefinedVariable
        self.assertEqual(EventType.ARRAY_START, events[0][0])
        self.assertEqual(EventType.ARRAY_END, events[1][0])
        
          
    @data(unpackc, unpackp)  
    def test_fixarray(self,f):
        bdata = msgpack.packb([1, 2, 3])
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(5, len(events))
        self.assertEqual(FormatType.FIXARRAY.value.code, events[0][1]) # @UndefinedVariable
        self.assertEqual(FormatType.POS_FIXINT.value.code, events[1][1]) # @UndefinedVariable
        self.assertEqual(FormatType.POS_FIXINT.value.code, events[2][1]) # @UndefinedVariable
        self.assertEqual(FormatType.POS_FIXINT.value.code, events[3][1]) # @UndefinedVariable
        self.assertEqual(FormatType.FIXARRAY.value.code, events[4][1]) # @UndefinedVariable
        
        self.assertEqual(EventType.ARRAY_START, events[0][0])
        self.assertEqual(EventType.VALUE, events[1][0])
        self.assertEqual(EventType.VALUE, events[2][0])
        self.assertEqual(EventType.VALUE, events[3][0])
        self.assertEqual(EventType.ARRAY_END, events[4][0])
        
        
        self.assertEqual(None, events[0][2])
        self.assertEqual(1, events[1][2])
        self.assertEqual(2, events[2][2])
        self.assertEqual(3, events[3][2])
        self.assertEqual(None, events[4][2])
    
    @data(unpackc, unpackp)
    def test_fixmap_empty(self,f):
        events = [e for e in f(self.create_instream(b'\x80'))]
        self.assertEqual( 2, len(events))
        self.assertEqual(FormatType.FIXMAP.value.code, events[0][1]) # @UndefinedVariable
        self.assertEqual(EventType.MAP_START, events[0][0])
        self.assertEqual(EventType.MAP_END, events[1][0])
        
        
    @data(unpackc, unpackp)
    def test_fixmap(self,f):
        bdata = msgpack.packb({"f1":1, "f2":2.2, "f3":'test'})
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(8, len(events))
        self.assertEqual(FormatType.FIXMAP.value.code, events[0][1]) # @UndefinedVariable
        self.assertEqual(FormatType.FIXSTR.value.code, events[1][1]) # @UndefinedVariable
        self.assertEqual(FormatType.POS_FIXINT.value.code, events[2][1]) # @UndefinedVariable
        self.assertEqual(FormatType.FIXSTR.value.code, events[3][1]) # @UndefinedVariable
        self.assertEqual(FormatType.FLOAT_64.value.code, events[4][1]) # @UndefinedVariable
        self.assertEqual(FormatType.FIXSTR.value.code, events[5][1]) # @UndefinedVariable
        self.assertEqual(FormatType.FIXSTR.value.code, events[6][1]) # @UndefinedVariable
        self.assertEqual(FormatType.FIXMAP.value.code, events[7][1]) # @UndefinedVariable
        self.assertEqual(EventType.MAP_START, events[0][0])
        self.assertEqual(EventType.MAP_PROPERTY_NAME, events[1][0])
        self.assertEqual(EventType.VALUE, events[2][0])
        self.assertEqual(EventType.MAP_PROPERTY_NAME, events[3][0])
        self.assertEqual(EventType.VALUE, events[4][0])
        self.assertEqual(EventType.MAP_PROPERTY_NAME, events[5][0])
        self.assertEqual(EventType.VALUE, events[6][0])
        self.assertEqual(EventType.MAP_END, events[7][0])
        
        
        self.assertEqual(None, events[0][2])
        self.assertEqual('f1', events[1][2])
        self.assertEqual(1, events[2][2])
        self.assertEqual('f2', events[3][2])
        self.assertEqual(2.2, events[4][2])
        self.assertEqual('f3', events[5][2])
        self.assertEqual('test', events[6][2])
        self.assertEqual(None, events[7][2])
        
    

   
    def create_instream(self, bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff
    
    
if __name__ == '__main__':
    unittest.main()

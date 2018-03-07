'''
Created on Nov 20, 2017

@author: Salim
'''

import unittest
from _io import BytesIO
from msgpackstream.defs import FormatType
from msgpackstream.backend.pyc.stream import unpack as unpackc
from msgpackstream.backend.python.stream import unpack as unpackp
from ddt import data,ddt
from msgpackstream.defs import EventType
import math
import msgpack



@ddt
class HeaderWithLengthValueTest(unittest.TestCase):


    @data(unpackc, unpackp)
    def test_str8_empty(self,f):
        events = [e for e in f(self.create_instream(b'\xD9\x00'))]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.STR_8.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual('', events[0][2])
        
    @data(unpackc, unpackp)
    def test_str8(self,f):
        bdata = self.create_instream(b'\xD9\x0Btest string')
        events = [e for e in f(bdata)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.STR_8.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual('test string', events[0][2])
        
    @data(unpackc, unpackp)
    def test_str16_empty(self, f):
        events = [e for e in f(self.create_instream(b'\xDA\x00\x00'))]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.STR_16.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual('', events[0][2])

    @data(unpackc, unpackp)                
    def test_str16(self, f):
        bdata = self.create_instream(b'\xDA\x00\x0Btest string')
        events = [e for e in f(bdata)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.STR_16.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual('test string', events[0][2])
    
    @data(unpackc, unpackp)    
    def test_str32_empty(self, f):
        events = [e for e in f(self.create_instream(b'\xDB\x00\x00\x00\x00'))]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.STR_32.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual('', events[0][2])
        
    @data(unpackc, unpackp)   
    def test_str32(self, f):
        bdata = self.create_instream(b'\xDB\x00\x00\x00\x0Btest string')
        events = [e for e in f(bdata)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.STR_32.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual('test string', events[0][2])
    
    @data(unpackc, unpackp)    
    def test_bin8_empty(self, f):
        events = [e for e in f(self.create_instream(b'\xC4\x00'))]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.BIN_8.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(b'', events[0][2])
    
    @data(unpackc, unpackp)    
    def test_bin8(self, f):
        bdata = self.create_instream(b'\xC4\x0Btest string')
        events = [e for e in f(bdata)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.BIN_8.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual('test string', events[0][2])
    
    @data(unpackc, unpackp)   
    def test_bin16_empty(self, f):
        events = [e for e in f(self.create_instream(b'\xC5\x00\x00'))]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.BIN_16.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(b'', events[0][2])
    
    @data(unpackc, unpackp)
    def test_bin16(self, f):
        bdata = self.create_instream(b'\xC5\x00\x0Btest string')
        events = [e for e in f(bdata)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.BIN_16.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual('test string', events[0][2])
    
    @data(unpackc, unpackp)    
    def test_bin32_empty(self, f):
        events = [e for e in f(self.create_instream(b'\xC6\x00\x00\x00\x00'))]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.BIN_32.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(b'', events[0][2])
    
    @data(unpackc, unpackp)    
    def test_bin32(self, f):
        bdata = self.create_instream(b'\xC6\x00\x00\x00\x0Btest string')
        events = [e for e in f(bdata)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.BIN_32.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual('test string', events[0][2])
    
    
    @data(unpackc, unpackp)
    def test_array16_empty(self, f):
        events = [e for e in f(self.create_instream(b'\xDC\x00\x00'))]
        self.assertEqual(2, len(events))
        self.assertEqual(FormatType.ARRAY_16.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(FormatType.ARRAY_16.value.code, events[-1][1])  # @UndefinedVariable
        
        
        
    @data(unpackc, unpackp)
    def test_array16(self,f):
        a = []
        for i in range(int(math.pow(2, 15))):
            a.append(1)
        
        events = [e for e in f(self.create_instream(msgpack.packb(a)))]
        
        self.assertEqual(len(a) + 2, len(events))
        
        self.assertEqual(FormatType.ARRAY_16.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(FormatType.ARRAY_16.value.code, events[-1][1])  # @UndefinedVariable
        
        self.assertEqual(EventType.ARRAY_START, events[0][0])
        self.assertEqual(EventType.ARRAY_END, events[-1][0])
        
        self.assertEqual(None, events[0][2])
        self.assertEqual(None, events[-1][2])
        
        for i in range(int(math.pow(2, 15))):
            self.assertEqual(EventType.VALUE, events[i + 1][0])
            self.assertEqual(FormatType.POS_FIXINT.value.code, events[i + 1][1])# @UndefinedVariable
            
    @data(unpackc, unpackp)
    def test_array32_empty(self,f):
        events = [e for e in f(self.create_instream(b'\xDD\x00\x00\x00\x00'))]
        self.assertEqual(2, len(events))
        
        self.assertEqual(FormatType.ARRAY_32.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(FormatType.ARRAY_32.value.code, events[-1][1])  # @UndefinedVariable
        
        
    @data(unpackc, unpackp)
    def test_array32(self,f):
        a = []
        for i in range(int(math.pow(2, 16))):
            a.append(1)
        
        events = [e for e in f(self.create_instream(msgpack.packb(a)))]
        
        self.assertEqual(len(a) + 2, len(events))
        
        self.assertEqual(FormatType.ARRAY_32.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(FormatType.ARRAY_32.value.code, events[-1][1])  # @UndefinedVariable
        
        self.assertEqual(EventType.ARRAY_START, events[0][0])
        self.assertEqual(EventType.ARRAY_END, events[-1][0])
        
        self.assertEqual(None, events[0][2])
        self.assertEqual(None, events[-1][2])
        
        for i in range(int(math.pow(2, 16))):
            self.assertEqual(EventType.VALUE, events[i + 1][0])
            self.assertEqual(FormatType.POS_FIXINT.value.code, events[i + 1][1])  # @UndefinedVariable
        
        
        
    @data(unpackc, unpackp)
    def test_map16_empty(self,f):
        events = [e for e in f(self.create_instream(b'\xDE\x00\x00'))]
        self.assertEqual(2, len(events))
        
        self.assertEqual(FormatType.MAP_16.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(FormatType.MAP_16.value.code, events[1][1])  # @UndefinedVariable
        
        self.assertEqual(EventType.MAP_START, events[0][0])
        self.assertEqual(EventType.MAP_END, events[1][0])
            
            
    @data(unpackc, unpackp)
    def test_map16(self,f):
        tmp = b'\xDE\x80\x00'
        length = int(math.pow(2, 15))
        for i in range(length):
            l = len(str(i)) + 1
            if l == 1:
                tmp += b'\xa1'
            elif l == 2:
                tmp += b'\xa2'
            elif l == 3:
                tmp += b'\xa3'
            elif l == 4:
                tmp += b'\xa4'
            elif l == 5:
                tmp += b'\xa5'
            elif l == 6:
                tmp += b'\xa6'    
            elif l == 6:
                tmp += b'\xa6' 
            tmp += b'f' + str(i) + b'\x01'
        
        events = [e for e in f(self.create_instream(tmp))]
        
#         print(events[-1])
        self.assertEqual(length * 2 + 2, len(events))
        
        self.assertEqual(FormatType.MAP_16.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(FormatType.MAP_16.value.code, events[-1][1])  # @UndefinedVariable
        
        self.assertEqual(EventType.MAP_START, events[0][0])
        self.assertEqual(EventType.MAP_END, events[-1][0])
        
        self.assertEqual(None, events[0][2])
        self.assertEqual(None, events[-1][2])
        
        for i in range(length * 2):
            if i % 2 is 0:
                self.assertEqual(EventType.MAP_PROPERTY_NAME, events[i + 1][0])
                self.assertEqual(FormatType.FIXSTR.value.code, events[i + 1][1])  # @UndefinedVariable
            else:
                self.assertEqual(EventType.VALUE, events[i + 1][0])
                self.assertEqual(FormatType.POS_FIXINT.value.code, events[i + 1][1])  # @UndefinedVariable
      
      
    @data(unpackc, unpackp)  
    def test_map32_empty(self,f):
        events = [e for e in f(self.create_instream(b'\xDF\x00\x00\x00\x00'))]
        self.assertEqual(2, len(events))
        
        self.assertEqual(FormatType.MAP_32.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(FormatType.MAP_32.value.code, events[1][1])  # @UndefinedVariable
        
        self.assertEqual(EventType.MAP_START, events[0][0])
        self.assertEqual(EventType.MAP_END, events[1][0])
        
            
    @data(unpackc, unpackp)
    def test_map32(self,f):
        length = int(math.pow(2, 16))
        a = {}
        for i in range(length):
            a['f' + str(i)] = 1
        
        events = [e for e in f(self.create_instream(msgpack.packb(a)))]
        
        self.assertEqual(len(a) * 2 + 2, len(events))
        
        self.assertEqual(FormatType.MAP_32.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(FormatType.MAP_32.value.code, events[-1][1])  # @UndefinedVariable
        
        self.assertEqual(EventType.MAP_START, events[0][0])
        self.assertEqual(EventType.MAP_END, events[-1][0])
        
        self.assertEqual(None, events[0][2])
        self.assertEqual(None, events[-1][2])
        
        for i in range(length * 2):
            if i % 2 is 0:
                self.assertEqual(EventType.MAP_PROPERTY_NAME, events[i + 1][0])
                self.assertEqual(FormatType.FIXSTR.value.code, events[i + 1][1])  # @UndefinedVariable
            else:
                self.assertEqual(EventType.VALUE, events[i + 1][0])
                self.assertEqual(FormatType.POS_FIXINT.value.code, events[i + 1][1])  # @UndefinedVariable
        
    

   
    def create_instream(self, bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff
    
    
if __name__ == '__main__':
    unittest.main()

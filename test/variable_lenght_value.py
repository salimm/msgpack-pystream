'''
Created on Nov 20, 2017

@author: Salim
'''

import unittest
from _io import BytesIO
import msgpackstream
from msgpackformat import FormatType
from msgpackstream import  EventType
import math
import msgpack



class HeaderWithLengthValueTest(unittest.TestCase):


    def test_str8_empty(self):
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(b'\xD9\x00'))]
        self.assertEqual(1, len(events))
        
        self.assertEqual(FormatType.STR_8, events[0][2])
        self.assertEqual('', events[0][3])
        
    def test_str8(self):
        bdata = self.create_instream(b'\xD9\x0Btest string')
        events = [e for e in msgpackstream.stream_unpack(bdata)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.STR_8, events[0][2])
        self.assertEqual(EventType.VALUE, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual('test string', events[0][3])
        
    def test_str16_empty(self):
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(b'\xDA\x00\x00'))]
        self.assertEqual(1, len(events))
        
        self.assertEqual(FormatType.STR_16, events[0][2])
        self.assertEqual('', events[0][3])
            
    def test_str16(self):
        bdata = self.create_instream(b'\xDA\x00\x0Btest string')
        events = [e for e in msgpackstream.stream_unpack(bdata)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.STR_16, events[0][2])
        self.assertEqual(EventType.VALUE, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual('test string', events[0][3])
        
    def test_str32_empty(self):
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(b'\xDB\x00\x00\x00\x00'))]
        self.assertEqual(1, len(events))
        
        self.assertEqual(FormatType.STR_32, events[0][2])
        self.assertEqual('', events[0][3])
        
        
    def test_str32(self):
        bdata = self.create_instream(b'\xDB\x00\x00\x00\x0Btest string')
        events = [e for e in msgpackstream.stream_unpack(bdata)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.STR_32, events[0][2])
        self.assertEqual(EventType.VALUE, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual('test string', events[0][3])
        
    def test_bin8_empty(self):
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(b'\xC4\x00'))]
        self.assertEqual(1, len(events))
        
        self.assertEqual(FormatType.BIN_8, events[0][2])
        self.assertEqual(b'', events[0][3])
        
    def test_bin8(self):
        bdata = self.create_instream(b'\xC4\x0Btest string')
        events = [e for e in msgpackstream.stream_unpack(bdata)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.BIN_8, events[0][2])
        self.assertEqual(EventType.VALUE, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual('test string', events[0][3])
        
    def test_bin16_empty(self):
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(b'\xC5\x00\x00'))]
        self.assertEqual(1, len(events))
        
        self.assertEqual(FormatType.BIN_16, events[0][2])
        self.assertEqual(b'', events[0][3])
    
    def test_bin16(self):
        bdata = self.create_instream(b'\xC5\x00\x0Btest string')
        events = [e for e in msgpackstream.stream_unpack(bdata)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.BIN_16, events[0][2])
        self.assertEqual(EventType.VALUE, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual('test string', events[0][3])
        
    def test_bin32_empty(self):
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(b'\xC6\x00\x00\x00\x00'))]
        self.assertEqual(1, len(events))
        
        self.assertEqual(FormatType.BIN_32, events[0][2])
        self.assertEqual(b'', events[0][3])
        
    def test_bin32(self):
        bdata = self.create_instream(b'\xC6\x00\x00\x00\x0Btest string')
        events = [e for e in msgpackstream.stream_unpack(bdata)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.BIN_32, events[0][2])
        self.assertEqual(EventType.VALUE, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual('test string', events[0][3])
    
    
        
    def test_array16_empty(self):
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(b'\xDC\x00\x00'))]
        self.assertEqual(2, len(events))
        
        self.assertEqual(FormatType.ARRAY_16, events[0][2])
        self.assertEqual(FormatType.ARRAY_16, events[-1][2])
        
        
        
    def test_array16(self):
        a = []
        for i in range(int(math.pow(2, 15))):
            a.append(1)
        
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(msgpack.packb(a)))]
        
        self.assertEqual(len(a) + 2, len(events))
        
        self.assertEqual(FormatType.ARRAY_16, events[0][2])
        self.assertEqual(FormatType.ARRAY_16, events[-1][2])
        
        self.assertEqual(EventType.ARRAY_START, events[0][1])
        self.assertEqual(EventType.ARRAY_END, events[-1][1])
        
        self.assertEqual(None, events[0][3])
        self.assertEqual(None, events[-1][3])
        
        for i in range(int(math.pow(2, 15))):
            self.assertEqual(['item'], events[i + 1][0])
            self.assertEqual(EventType.VALUE, events[i + 1][1])
            self.assertEqual(FormatType.POS_FIXINT, events[i + 1][2])
            
    def test_array32_empty(self):
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(b'\xDD\x00\x00\x00\x00'))]
        self.assertEqual(2, len(events))
        
        self.assertEqual(FormatType.ARRAY_32, events[0][2])
        self.assertEqual(FormatType.ARRAY_32, events[-1][2])
        
        
    def test_array32(self):
        a = []
        for i in range(int(math.pow(2, 16))):
            a.append(1)
        
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(msgpack.packb(a)))]
        
        self.assertEqual(len(a) + 2, len(events))
        
        self.assertEqual(FormatType.ARRAY_32, events[0][2])
        self.assertEqual(FormatType.ARRAY_32, events[-1][2])
        
        self.assertEqual(EventType.ARRAY_START, events[0][1])
        self.assertEqual(EventType.ARRAY_END, events[-1][1])
        
        self.assertEqual(None, events[0][3])
        self.assertEqual(None, events[-1][3])
        
        for i in range(int(math.pow(2, 16))):
            self.assertEqual(['item'], events[i + 1][0])
            self.assertEqual(EventType.VALUE, events[i + 1][1])
            self.assertEqual(FormatType.POS_FIXINT, events[i + 1][2])
        
        
        
    def test_map16_empty(self):
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(b'\xDE\x00\x00'))]
        self.assertEqual(2, len(events))
        
        self.assertEqual(FormatType.MAP_16, events[0][2])
        self.assertEqual(FormatType.MAP_16, events[1][2])
        
        self.assertEqual(EventType.MAP_START, events[0][1])
        self.assertEqual(EventType.MAP_END, events[1][1])
            
            
    def test_map16(self):
        length = int(math.pow(2, 15))
        a = {}
        for i in range(length):
            a['f' + str(i)] = 1
        
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(msgpack.packb(a)))]
        
        self.assertEqual(len(a)*2 + 2, len(events))
        
        self.assertEqual(FormatType.MAP_16, events[0][2])
        self.assertEqual(FormatType.MAP_16, events[-1][2])
        
        self.assertEqual(EventType.MAP_START, events[0][1])
        self.assertEqual(EventType.MAP_END, events[-1][1])
        
        self.assertEqual(None, events[0][3])
        self.assertEqual(None, events[-1][3])
        
        field = None;
        for i in range(length*2):
            if i % 2 is 0:
                self.assertEqual([], events[i + 1][0])
                self.assertEqual(EventType.MAP_PROPERTY_NAME, events[i + 1][1])
                self.assertEqual(FormatType.FIXSTR, events[i + 1][2])
                field = events[i + 1][3]
            else:
                self.assertEqual([field], events[i + 1][0])
                self.assertEqual(EventType.VALUE, events[i + 1][1])
                self.assertEqual(FormatType.POS_FIXINT, events[i+ 1][2])
        
    def test_map32_empty(self):
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(b'\xDF\x00\x00\x00\x00'))]
        self.assertEqual(2, len(events))
        
        self.assertEqual(FormatType.MAP_32, events[0][2])
        self.assertEqual(FormatType.MAP_32, events[1][2])
        
        self.assertEqual(EventType.MAP_START, events[0][1])
        self.assertEqual(EventType.MAP_END, events[1][1])
        
            
    def test_map32(self):
        length = int(math.pow(2, 16))
        a = {}
        for i in range(length):
            a['f' + str(i)] = 1
        
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(msgpack.packb(a)))]
        
        self.assertEqual(len(a)*2 + 2, len(events))
        
        self.assertEqual(FormatType.MAP_32, events[0][2])
        self.assertEqual(FormatType.MAP_32, events[-1][2])
        
        self.assertEqual(EventType.MAP_START, events[0][1])
        self.assertEqual(EventType.MAP_END, events[-1][1])
        
        self.assertEqual(None, events[0][3])
        self.assertEqual(None, events[-1][3])
        
        field = None;
        for i in range(length*2):
            if i % 2 is 0:
                self.assertEqual([], events[i + 1][0])
                self.assertEqual(EventType.MAP_PROPERTY_NAME, events[i + 1][1])
                self.assertEqual(FormatType.FIXSTR, events[i + 1][2])
                field = events[i + 1][3]
            else:
                self.assertEqual([field], events[i + 1][0])
                self.assertEqual(EventType.VALUE, events[i + 1][1])
                self.assertEqual(FormatType.POS_FIXINT, events[i+ 1][2])
        
    

   
    def create_instream(self, bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff
    
    
if __name__ == '__main__':
    unittest.main()

'''
Created on Nov 21, 2017

@author: Salim
'''
import unittest
from _io import BytesIO
import msgpackstream.stream as msgpackapi
from msgpackstream.format import FormatType, ExtType
from msgpackstream.stream import  EventType, ExtTypeParser


class TestExtParser(ExtTypeParser):
    
    def deserialize(self, exttype, buff, start , end):
        return (end-start)
    
    def handled_extcode(self):
        return 2
    
    
class TestExtFormats(unittest.TestCase):
    
    
        
    def test_fixext1_raw(self):
        buff = self.create_instream(b'\xd4\x01\x00')
        events = [e for e in msgpackapi.unpack(buff)]
        
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_1,1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'\x00', events[0][3])
    

    def test_fixext2_raw(self):
        buff = self.create_instream(b'\xd5\x01\x00\x00')
        events = [e for e in msgpackapi.unpack(buff)]
        
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_2,1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'\x00\x00', events[0][3])
        
    
    def test_fixext4_raw(self):
        buff = self.create_instream(b'\xd6\x01\x00\x00\x00\x00')
        events = [e for e in msgpackapi.unpack(buff)]
        
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_4,1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'\x00\x00\x00\x00', events[0][3])
        
        
    def test_fixext8_raw(self):
        buff = self.create_instream(b'\xd7\x01\x00\x00\x00\x00\x00\x00\x00\x00')
        events = [e for e in msgpackapi.unpack(buff)]
        
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_8,1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'\x00\x00\x00\x00\x00\x00\x00\x00', events[0][3])
        
    def test_fixext16_raw(self):
        buff = self.create_instream(b'\xd8\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        events = [e for e in msgpackapi.unpack(buff)]
        
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_16,1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', events[0][3])
        
    def test_ext8_raw(self):
        buff = self.create_instream(b'\xc7\x03\x01\x00\x00\x00')
        events = [e for e in msgpackapi.unpack(buff)]
        
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_8,1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'\x00\x00\x00', events[0][3])
        
    def test_ext8_empty(self):
        buff = self.create_instream(b'\xc7\x00\x01')
        events = [e for e in msgpackapi.unpack(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_8,1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'', events[0][3])
        
        
    def test_ext16_raw(self):
        buff = self.create_instream(b'\xc8\x00\x03\x01\x00\x00\x00')
        events = [e for e in msgpackapi.unpack(buff)]
        
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_16,1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'\x00\x00\x00', events[0][3])
        
    def test_ext16_empty(self):
        buff = self.create_instream(b'\xc8\x00\x00\x01')
        events = [e for e in msgpackapi.unpack(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_16,1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'', events[0][3])
        
    def test_ext32_raw(self):
        buff = self.create_instream(b'\xc9\x00\x00\x00\x03\x01\x00\x00\x00')
        events = [e for e in msgpackapi.unpack(buff)]
        
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_32,1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'\x00\x00\x00', events[0][3])
        
    def test_ext32_empty(self):
        buff = self.create_instream(b'\xc9\x00\x00\x00\x00\x01')
        events = [e for e in msgpackapi.unpack(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_32,1), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'', events[0][3])
        
    
        
    def test_fixext1(self):
        buff = self.create_instream(b'\xd4\x02\x00')
        customerparser = TestExtParser()
        events = [e for e in msgpackapi.unpack(buff,parsers=[customerparser])]
        
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_1,2), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(1, events[0][3])    
    
    def test_ext8(self):
        buff = self.create_instream(b'\xc7\x03\x02\x00\x00\x00')
        customerparser = TestExtParser()
        events = [e for e in msgpackapi.unpack(buff,parsers=[customerparser])]
        
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_8,2), events[0][2])
        self.assertEqual(EventType.EXT, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(3, events[0][3])
        
    
    
        

    def create_instream(self, bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff    
    
    
if __name__ == '__main__':
    unittest.main()
    
    

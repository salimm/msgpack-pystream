'''
Created on Nov 21, 2017

@author: Salim
'''
import unittest
import msgpack
from _io import BytesIO
import msgpackstream
from msgpackformat import FormatType
from msgpackstream import  EventType



class TestExtFormats(unittest.TestCase):
    
    
        
    def test_fixext1_raw(self):
        buff = self.create_instream(b'\xd4\x01\x00')
        events = [e for e in msgpackstream.stream_unpack(buff)]
        
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.FIXEXT_1, events[0][2])
        self.assertEqual(EventType.VALUE, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'\x00', events[0][3])
    

    def test_fixext2_raw(self):
        buff = self.create_instream(b'\xd5\x01\x00\x00')
        events = [e for e in msgpackstream.stream_unpack(buff)]
        
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.FIXEXT_2, events[0][2])
        self.assertEqual(EventType.VALUE, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'\x00\x00', events[0][3])
        
    
    def test_fixext4_raw(self):
        buff = self.create_instream(b'\xd6\x01\x00\x00\x00\x00')
        events = [e for e in msgpackstream.stream_unpack(buff)]
        
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.FIXEXT_4, events[0][2])
        self.assertEqual(EventType.VALUE, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'\x00\x00\x00\x00', events[0][3])
        
        
    def test_fixext8_raw(self):
        buff = self.create_instream(b'\xd7\x01\x00\x00\x00\x00\x00\x00\x00\x00')
        events = [e for e in msgpackstream.stream_unpack(buff)]
        
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.FIXEXT_8, events[0][2])
        self.assertEqual(EventType.VALUE, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'\x00\x00\x00\x00\x00\x00\x00\x00', events[0][3])
        
    def test_fixext16_raw(self):
        buff = self.create_instream(b'\xd8\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        events = [e for e in msgpackstream.stream_unpack(buff)]
        
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.FIXEXT_16, events[0][2])
        self.assertEqual(EventType.VALUE, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', events[0][3])

    def create_instream(self, bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff    
    
    
if __name__ == '__main__':
    unittest.main()
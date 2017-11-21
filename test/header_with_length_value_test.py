'''
Created on Nov 20, 2017

@author: Salim
'''

import unittest
import msgpack
from _io import BytesIO
import msgpackstream
from msgpackformat import FormatType
from msgpackstream import  EventType



class HeaderWithLengthValueTest(unittest.TestCase):

    def test_fixst_empty(self):
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(b'\xA0'))]
        self.assertEqual( 1, len(events))
        
        self.assertEqual(FormatType.FIXSTR, events[0][2])
        self.assertEqual('', events[0][3])

    def test_fixstr(self):
        bdata = msgpack.packb('test string')
        buff = self.create_instream(bdata)
        events = [e for e in msgpackstream.stream_unpack(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.FIXSTR, events[0][2])
        self.assertEqual(EventType.VALUE, events[0][1])
        self.assertEqual([], events[0][0])
        self.assertEqual('test string', events[0][3])
        
    def test_fixarrray_empty(self):
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(b'\x90'))]
        self.assertEqual( 2, len(events))
        
        self.assertEqual(FormatType.FIXARRAY, events[0][2])
        self.assertEqual(EventType.ARRAY_START, events[0][1])
        self.assertEqual(EventType.ARRAY_END, events[1][1])
        
            
    def test_fixarray(self):
        bdata = msgpack.packb([1, 2, 3])
        buff = self.create_instream(bdata)
        events = [e for e in msgpackstream.stream_unpack(buff)]
        self.assertEqual(5, len(events))
        
        self.assertEqual(FormatType.FIXARRAY, events[0][2])
        self.assertEqual(FormatType.POS_FIXINT, events[1][2])
        self.assertEqual(FormatType.POS_FIXINT, events[2][2])
        self.assertEqual(FormatType.POS_FIXINT, events[3][2])
        self.assertEqual(FormatType.FIXARRAY, events[4][2])
        
        self.assertEqual(EventType.ARRAY_START, events[0][1])
        self.assertEqual(EventType.VALUE, events[1][1])
        self.assertEqual(EventType.VALUE, events[2][1])
        self.assertEqual(EventType.VALUE, events[3][1])
        self.assertEqual(EventType.ARRAY_END, events[4][1])
        
        self.assertEqual([], events[0][0])
        self.assertEqual(['item'], events[1][0])
        self.assertEqual(['item'], events[2][0])
        self.assertEqual(['item'], events[3][0])
        self.assertEqual([], events[4][0])
        
        self.assertEqual(None, events[0][3])
        self.assertEqual(1, events[1][3])
        self.assertEqual(2, events[2][3])
        self.assertEqual(3, events[3][3])
        self.assertEqual(None, events[4][3])
    
    def test_fixmap_empty(self):
        events = [e for e in msgpackstream.stream_unpack(self.create_instream(b'\x80'))]
        self.assertEqual( 2, len(events))
        
        self.assertEqual(FormatType.FIXMAP, events[0][2])
        self.assertEqual(EventType.MAP_START, events[0][1])
        self.assertEqual(EventType.MAP_END, events[1][1])
        
        
    def test_fixmap(self):
        bdata = msgpack.packb({"f1":1, "f2":2.2, "f3":'test'})
        buff = self.create_instream(bdata)
        events = [e for e in msgpackstream.stream_unpack(buff)]
        self.assertEqual(8, len(events))
        
        self.assertEqual(FormatType.FIXMAP, events[0][2])
        self.assertEqual(FormatType.FIXSTR, events[1][2])
        self.assertEqual(FormatType.POS_FIXINT, events[2][2])
        self.assertEqual(FormatType.FIXSTR, events[3][2])
        self.assertEqual(FormatType.FLOAT_64, events[4][2])
        self.assertEqual(FormatType.FIXSTR, events[5][2])
        self.assertEqual(FormatType.FIXSTR, events[6][2])
        self.assertEqual(FormatType.FIXMAP, events[7][2])
        
        self.assertEqual(EventType.MAP_START, events[0][1])
        self.assertEqual(EventType.MAP_PROPERTY_NAME, events[1][1])
        self.assertEqual(EventType.VALUE, events[2][1])
        self.assertEqual(EventType.MAP_PROPERTY_NAME, events[3][1])
        self.assertEqual(EventType.VALUE, events[4][1])
        self.assertEqual(EventType.MAP_PROPERTY_NAME, events[5][1])
        self.assertEqual(EventType.VALUE, events[6][1])
        self.assertEqual(EventType.MAP_END, events[7][1])
        
        self.assertEqual([], events[0][0])
        self.assertEqual([], events[1][0])
        self.assertEqual(['f1'], events[2][0])
        self.assertEqual([], events[3][0])
        self.assertEqual(['f2'], events[4][0])
        self.assertEqual([], events[5][0])
        self.assertEqual(['f3'], events[6][0])
        self.assertEqual([], events[7][0])
        
        self.assertEqual(None, events[0][3])
        self.assertEqual('f1', events[1][3])
        self.assertEqual(1, events[2][3])
        self.assertEqual('f2', events[3][3])
        self.assertEqual(2.2, events[4][3])
        self.assertEqual('f3', events[5][3])
        self.assertEqual('test', events[6][3])
        self.assertEqual(None, events[7][3])
        
    

   
    def create_instream(self, bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff
    
    
if __name__ == '__main__':
    unittest.main()

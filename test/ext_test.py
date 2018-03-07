'''
Created on Nov 21, 2017

@author: Salim
'''
import unittest
from _io import BytesIO
from  msgpackstream.backend.python.stream import unpack as unpackp
from  msgpackstream.backend.pyc.stream import unpack as unpackc
from ddt import data,ddt
from msgpackstream.defs import EventType, ExtType,FormatType, ExtTypeParser



class TestExtParser(ExtTypeParser):
    
    def deserialize(self, exttype, buff, start , end):
        return (end-start)
    
    def handled_extcode(self):
        return 2
    



@ddt
class TestExtFormats(unittest.TestCase):
    '''
    
    '''
    
    
    @data(unpackc, unpackp)
    def test_fixext1_raw(self,f):
        buff = self.create_instream(b'\xd4\x01\x00')
        events = [e for e in f(buff)]
        
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_1.value.code,1), events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(b'\x00', events[0][2])
    
  
    @data(unpackc, unpackp)
    def test_fixext2_raw(self,f):
        buff = self.create_instream(b'\xd5\x01\x00\x00')
        events = [e for e in f(buff)]
         
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_2.value.code,1), events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(b'\x00\x00', events[0][2])
   
         
    @data(unpackc, unpackp)
    def test_fixext4_raw(self,f):
        buff = self.create_instream(b'\xd6\x01\x00\x00\x00\x00')
        events = [e for e in f(buff)]
         
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_4.value.code,1), events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(b'\x00\x00\x00\x00', events[0][2])
         
     
    @data(unpackc, unpackp)    
    def test_fixext8_raw(self,f):
        buff = self.create_instream(b'\xd7\x01\x00\x00\x00\x00\x00\x00\x00\x00')
        events = [e for e in f(buff)]
         
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_8.value.code,1), events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(b'\x00\x00\x00\x00\x00\x00\x00\x00', events[0][2])
    
     
    @data(unpackc, unpackp)    
    def test_fixext16_raw(self,f):
        buff = self.create_instream(b'\xd8\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        events = [e for e in f(buff)]
         
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_16.value.code,1), events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', events[0][2])
 
     
    @data(unpackc, unpackp)    
    def test_ext8_raw(self,f):
        buff = self.create_instream(b'\xc7\x03\x01\x00\x00\x00')
        events = [e for e in f(buff)]
         
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_8.value.code,1), events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(b'\x00\x00\x00', events[0][2])
    
     
    @data(unpackc, unpackp)    
    def test_ext8_empty(self,f):
        buff = self.create_instream(b'\xc7\x00\x01')
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_8.value.code,1), events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(b'', events[0][2])
  
         
    @data(unpackc, unpackp)    
    def test_ext16_raw(self,f):
        buff = self.create_instream(b'\xc8\x00\x03\x01\x00\x00\x00')
        events = [e for e in f(buff)]
         
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_16.value.code,1), events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(b'\x00\x00\x00', events[0][2])
  
     
    @data(unpackc, unpackp)    
    def test_ext16_empty(self,f):
        buff = self.create_instream(b'\xc8\x00\x00\x01')
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_16.value.code,1), events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(b'', events[0][2])
     
    @data(unpackc, unpackp)    
    def test_ext32_raw(self,f):
        buff = self.create_instream(b'\xc9\x00\x00\x00\x03\x01\x00\x00\x00')
        events = [e for e in f(buff)]
         
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_32.value.code,1), events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(b'\x00\x00\x00', events[0][2])
   
     
    @data(unpackc, unpackp)    
    def test_ext32_empty(self,f):
        buff = self.create_instream(b'\xc9\x00\x00\x00\x00\x01')
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_32.value.code,1), events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(b'', events[0][2])
         
    
     
    @data(unpackc, unpackp)    
    def test_fixext1(self,f):
        buff = self.create_instream(b'\xd4\x02\x00')
        customerparser = TestExtParser()
        events = [e for e in f(buff,parsers=[customerparser])]
         
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.FIXEXT_1.value.code,2), events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(1, events[0][2])    
     
     
    @data(unpackc, unpackp)
    def test_ext8(self,f):
        buff = self.create_instream(b'\xc7\x03\x02\x00\x00\x00')
        customerparser = TestExtParser()
        events = [e for e in f(buff,parsers=[customerparser])]
         
        self.assertEqual(1, len(events))
        self.assertEqual(ExtType(FormatType.EXT_8.value.code,2), events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.EXT, events[0][0])
        self.assertEqual(3, events[0][2])
         
     
    
        

    def create_instream(self, bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff    
    
    
if __name__ == '__main__':
    unittest.main()
    
    

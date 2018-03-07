'''
Created on Nov 20, 2017

@author: Salim
'''
import unittest
import msgpack
from _io import BytesIO
from msgpackstream.backend.pyc.stream import unpack as unpackc
from msgpackstream.backend.python.stream import unpack as unpackp
from msgpackstream.defs import EventType, FormatType
from ddt import ddt, data



@ddt
class TestSingleByteTypes(unittest.TestCase):

    @data(unpackc, unpackp)
    def test_nil(self, f):
        bdata = msgpack.packb(None)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.NIL.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0]) 
        self.assertEqual(None, events[0][2])
        

    @data(unpackc, unpackp)
    def test_pos_fixint(self,f):
        # checking min
        bdata = msgpack.packb(1)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.POS_FIXINT.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(1, events[0][2])
        
        # checking max 
        bdata = msgpack.packb(127)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.POS_FIXINT.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(127, events[0][2])


    @data(unpackc, unpackp)
    def test_boolean(self, f):
        # checking min
        bdata = msgpack.packb(False)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.FALSE.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(False, events[0][2])
        
        # checking max 
        bdata = msgpack.packb(True)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.TRUE.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(True, events[0][2])
        
    @data(unpackc, unpackp)
    def test_negfixint(self,f):
        # checking min
        bdata = msgpack.packb(-1)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.NEG_FIXINT.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(-1, events[0][2])
        
        # checking max 
        bdata = msgpack.packb(-15)
        buff = self.create_instream(bdata)
        events = [e for e in f(buff)]
        self.assertEqual(1, len(events))
        self.assertEqual(FormatType.NEG_FIXINT.value.code, events[0][1])  # @UndefinedVariable
        self.assertEqual(EventType.VALUE, events[0][0])
        self.assertEqual(-15, events[0][2])
    
    def create_instream(self, bdata):
        buff = BytesIO()
        buff.write(bdata)
        buff.seek(0)
        return buff
    
    
if __name__ == '__main__':
    unittest.main()

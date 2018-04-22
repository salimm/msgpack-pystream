'''
Created on Nov 13, 2017

@author: Salim
'''
from _pyio import __metaclass__
 
from msgpackstream.defs import  TimestampParser    
from msgpackstream.backend.python.format import FormatUtil
from msgpackstream.backend.python.stream import ScannerState
from mpstream_cunpacker import process , create_eventstream





class StreamUnpacker():
    '''
        StreamUnpacker provides a SAX-like unpacker that reads the input in stream and in batches. It will generate events accordingly. 
    ''' 
    def __init__(self):  
        self._stack = []
        self._scstate = ScannerState.IDLE
        self._state = None
        self._util = FormatUtil();
        self._events = []
        self._memory = ''
        self._deserializers = {}
        self.register(TimestampParser())
        self._waitingforprop = 0
        self._parentismap = 0
        self.scstatelist = [ScannerState.IDLE, ScannerState.WAITING_FOR_HEADER, ScannerState.WAITING_FOR_EXT_TYPE, ScannerState.WAITING_FOR_LENGTH, ScannerState.WAITING_FOR_VALUE, ScannerState.SEGMENT_ENDED]
        
    
    def process(self, buff):
        '''
            Process the input buffer. The buffer can contains all or a segment of the bytes from the complete message. 
            The function will buffer what will require extra bytes to be processed. 
        :param buff:
        '''
        (self._stack, self._memory, scstateidx, self._state, 
            tmpevents, self._waitingforprop, self._parentismap) = process( buff, self.create_parser_info(), self._deserializers);
        self._scstate = self.scstatelist[scstateidx-1]
        
        self._events = tmpevents
        
    def create_parser_info(self):
        return (self._stack, self._memory, self._scstate.value, self._state, self._events, self._waitingforprop, self._parentismap, len(self._memory));
        
        
    def generate_events(self):
        '''
            returns the generated events for the given segment of bytes
        '''
        tmp = self._events
        self._events = []
        return tmp
    

    def register(self, parser):
        self._deserializers[parser.handled_extcode()] = parser
    
        
        
    
def UnpackerIterator(instream, buffersize=5000, parsers=[]):
    deserializers = {};
    for parser in parsers:
        deserializers[parser.handled_extcode()] = parser
    tsparser = TimestampParser()
    deserializers[tsparser.handled_extcode()] = tsparser;    
    return  create_eventstream(instream, buffersize, deserializers)
        
    

def unpack(instream, buffersize=5000, parsers=[]):
    '''``
        Creates an iterator instance for the unpacker
    :param instream:
    :param buffersize:
    '''
    return UnpackerIterator(instream, buffersize, parsers)
    
    
    

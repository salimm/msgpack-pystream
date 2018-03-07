'''
Created on Nov 13, 2017

@author: Salim
'''
from _pyio import __metaclass__
 
from msgpackstream.defs import SegmentType, FormatType, ValueType, EventType, ExtType  , \
    TimestampParser, Format
from msgpackstream.backend.python.format import FormatUtil
from msgpackstream.backend.python.stream import ScannerState
import mpstream_cunpacker 






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
        self.eventlist = [EventType.VALUE, EventType.ARRAY_START, EventType.ARRAY_END, EventType.MAP_START, EventType.MAP_END, EventType.MAP_PROPERTY_NAME, EventType.EXT]
        self.scstatelist = [ScannerState.IDLE, ScannerState.WAITING_FOR_HEADER, ScannerState.WAITING_FOR_EXT_TYPE, ScannerState.WAITING_FOR_LENGTH, ScannerState.WAITING_FOR_VALUE, ScannerState.SEGMENT_ENDED]
        
    
    def process(self, buff):
        '''
            Process the input buffer. The buffer can contains all or a segment of the bytes from the complete message. 
            The function will buffer what will require extra bytes to be processed. 
        :param buff:
        '''
        (self._stack, self._memory, scstateidx, self._state, 
            tmpevents, self._waitingforprop, self._parentismap) = mpstream_cunpacker.process( buff, self.create_parser_info());
        self._scstate = self.scstatelist[scstateidx-1]
        
#         self._events = tmpevents #self.transform_events(tmpevents)
        self._events = self.transform_events(tmpevents);
        
        
        
    def transform_events(self, tmpevents):
        out = []        
        for x in range(0, len(tmpevents)):
            ev = tmpevents[x]
            o = None            
            if ev[1][1] is None:
                o = (self.eventlist[ev[0]-1], ev[1][0], ev[2])
            else:
                exttype = ExtType(ev[1][0],ev[1][1])
                val= ev[2]
                parser = self._deserializers.get(exttype.extcode, None)
                if parser:
                    val =  parser.deserialize(exttype, val, 0   , len(val))
                o = (self.eventlist[ev[0]-1],exttype , val)
#              
            out.append(o)
             
        return out
            
        
    def create_parser_info(self):
        return (self._stack, self._memory, self._scstate.value, self._state, self._events, self._waitingforprop, self._parentismap);
        
        
    def generate_events(self):
        '''
            returns the generated events for the given segment of bytes
        '''
        tmp = self._events
        self._events = []
        return tmp
    

    def register(self, parser):
        self._deserializers[parser.handled_extcode()] = parser
    
        
        
        
        
    
    
    
class UnpackerIterator(object):
    
    def __init__(self, instream, buffersize=5000, parsers=[]):
        self._instream = instream
        self._unpacker = StreamUnpacker()
        for parser in parsers:
            self._unpacker.register(parser)
        self._buffersize = buffersize
        self._events = []
        self._idx = 0
        
    
    def __iter__(self):
        return self

    def __next__(self):
        if self._idx >= len(self._events):
            self._events = []
            while len(self._events) is 0:
                self._idx = 0
                bytes_read = self._instream.read(self._buffersize)
                if not bytes_read:
                    raise StopIteration()
                self._unpacker.process(bytes_read)
                self._events = self._unpacker.generate_events()
        event = self._events[self._idx]
        self._idx = self._idx + 1 
        return event
        
        

    next = __next__  # Python 2   
    
    
    

def unpack(instream, buffersize=4000, parsers=[]):
    '''``
        Creates an iterator instance for the unpacker
    :param instream:
    :param buffersize:
    '''
    return UnpackerIterator(instream, buffersize, parsers)
    
    
    

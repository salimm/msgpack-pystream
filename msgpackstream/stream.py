'''
Created on Nov 13, 2017

@author: Salim
'''
from _pyio import __metaclass__
from abc import ABCMeta, abstractmethod
from enum import Enum
import struct
from msgpackstream.format import FormatUtil, SegmentType, FormatType, ValueType
from msgpackstream.errors import InvalidStateException
from _io import BytesIO



class StreamUnpacker():
    
    def __init__(self):        
        self._stack = []
        self._scstate = ScannerState.IDLE
        self._state = None
        self.util = FormatUtil();
        self.prefix = []
        self.events = []
        self.memory = BytesIO()
        self.lastidx = 0;
        
    
    
    def process(self, buff):
        idx = self.memory.tell()
        self.memory.write(buff)
        self.memory.seek(idx)
                
        
        byte = self.memory.read(1)
        while byte:
            print(str(self.lastidx) + ' - ' + str(idx))
            print(self._scstate)
            print(self._state)
            print(byte)
            byte = ord(byte)
            print(hex(byte))
            
            event = None
            if self._scstate in [ScannerState.IDLE, ScannerState.WAITING_FOR_HEADER]:                
                event = self.handle_read_header(byte)
                self.lastidx = idx + 1
            elif self._scstate is ScannerState.WAITING_FOR_LENGTH:
                self._state.remaining -= 1;  # decrease number of remaining bytes to get length
                if(self._state.remaining == 0):  # if no more bytes remaining
                    self.handle_read_length(self.memory, self.lastidx, idx + 1)
                    self.lastidx = idx +1
                    if self._state.template.value.valuetype is ValueType.NESTED:
                        self.push_state()
            elif self._scstate is ScannerState.WAITING_FOR_VALUE:
                self._state.remaining -= 1;                
                if(self._state.remaining == 0):
                    event = self.handle_read_value(self.memory, self.lastidx, idx + 1)
                    self.lastidx = idx +1
            elif self._scstate is ScannerState.WAITING_FOR_EXT_TYPE:
                pass            
            
            if self._scstate is ScannerState.SEGMENT_ENDED:
                self.handle_segment_ended()
            
            if event is not None:
                self.events.append(event)
            
            idx = idx + 1
            byte = self.memory.read(1)
        
        
        # not finished processing all since it needed extra info     
        if self.lastidx is idx:
            self.memory = BytesIO()
            self.lastidx = 0
    
    def handle_segment_ended(self):                           
        print(self._scstate)
        if(len(self._stack) == 0):
            self._scstate = ScannerState.IDLE
            return 
        self._scstate = ScannerState.WAITING_FOR_HEADER
        self.pop_state()
        
        if self._state.remaining == 0:
            self.handle_segment_ended()
            
        
    
    def handle_read_length(self, buff, start, end):        
        self._state.length = self.parse_int(buff, start, end)
    
        if self.current_state().template.value.valuetype is ValueType.NESTED:
            self._scstate = ScannerState.WAITING_FOR_HEADER
            self.push_state()
        else:
            self._scstate = ScannerState.WAITING_FOR_VALUE    
        
    
    def handle_read_value(self, buff, start, end):
        segmenttype = self._state.template.value.segmenttype
        # parsing value 
        if segmenttype in [SegmentType.HEADER_VALUE_PAIR, SegmentType.VARIABLE_LENGTH_VALUE, SegmentType.HEADER_WITH_LENGTH_VALUE_PAIR]:
            self._scstate = ScannerState.SEGMENT_ENDED
            value = self.parse_value(self._state.formattype, buff, start, end)
            return (self.prefix, EventType.VALUE, self._state.formattype, value)
        # next we should expect length
        elif segmenttype in [SegmentType.FIXED_EXT_FORMAT, SegmentType.EXT_FORMAT]:
            return (self.prefix, EventType.EXT, self._state.formattype, buff[start:end])
        else:
            raise InvalidStateException(self._scstate, "header")
                  
    
    def handle_read_header(self, byte):
        frmt = self.util.find(byte)
        template = self.util.find_template(frmt.value.code)
        segmenttype = template.value.segmenttype        

        print(frmt)
        
        # single byte segment
        if segmenttype is SegmentType.SINGLE_BYTE:
            self._scstate = ScannerState.SEGMENT_ENDED
            self._state = ParserState(frmt, template, isdone=True);
            return (self.prefix, EventType.VALUE, frmt, self.util.get_value(byte, frmt))
        # next we should expect value
        elif segmenttype is SegmentType.HEADER_VALUE_PAIR:
            self._scstate = ScannerState.WAITING_FOR_VALUE
            self._state = ParserState(frmt, template, length=template.value.length , isdone=False);            
        # next we should expect value
        elif segmenttype is SegmentType.HEADER_WITH_LENGTH_VALUE_PAIR:
            self._state = ParserState(frmt, template, length=self.util.get_value(byte, frmt) , isdone=False);
            if self._state.template.value.valuetype is ValueType.NESTED:
                self._scstate = ScannerState.WAITING_FOR_HEADER
            else:                
                self._scstate = ScannerState.WAITING_FOR_VALUE
            
        # next we should expect length
        elif segmenttype is SegmentType.VARIABLE_LENGTH_VALUE:
            self._scstate = ScannerState.WAITING_FOR_LENGTH
            self._state = ParserState(frmt, template, length=template.value.length , isdone=False);
        # next we should expect length
        elif segmenttype is SegmentType.EXT_FORMAT:
            self._scstate = ScannerState.WAITING_FOR_LENGTH
        # next we should expect type       
        elif segmenttype is SegmentType.FIXED_EXT_FORMAT:
            self._scstate = ScannerState.WAITING_FOR_EXT_TYPE
        else:
            raise InvalidStateException(self._scstate, "header")
        
    def push_state(self):
        self._stack.append(self._state)
        self._state = None
        
    def pop_state(self):
        self._state = self._stack.pop()
        self._state.remaining = self._state.remaining -1
         
                    
    def parse_int(self, buff, start, end):
        buff.seek(start)
        l = (end - start)
        print("------" + str(l))
        num = 0
        for i in range(l):
            byte = ord(buff.read(1))
            print(byte)
            num = num | byte << (l - i - 1) * 8
            print(num)
        return num
    
    def parse_value(self, formattype, buff, start, end):
        if(formattype in [FormatType.STR_16, FormatType.STR_8, FormatType.STR_32, FormatType.FIXSTR]):
            return self.parse_str(buff, start, end)
        pass
    
    def parse_str(self, buff, start, end):
        buff.seek(start)
        return buff.read((end - start)) 
    
    
    def generate_events(self):
        tmp = self.events
        self.events = []
        return tmp
    
    def current_state(self):
        return self._state
    
        
    state = property(current_state)
    
    

class EventType(Enum):
    
    VALUE = 1
    STR_START = 2
    STR_END = 3
    BIN_START = 4
    BIN_END = 5
    ARRAY_START = 6
    ARRAY_END = 7
    MAP_START = 8
    MAP_END = 9
    MAP_PROPERTY_NAME = 10
    EXT = 11  
    
    
class ParserState():
    
        def __init__(self, formattype, template, length=None, isdone=False):
            self.formattype = formattype
            self.template = template
            self._length = length
            self.remaining = length
            self.isdone = isdone
            
            
        def set_length(self, length):
            self._length = length
            self.remaining = length
        
        def get_length(self):
            return self._length 
            
        length = property(get_length, set_length)
        
        def __str__(self):
            return "ParserState formattype: " + str(self.formattype) + ", tempalte: " + str(self.template) + ", length: " + str(self.length) + ", remaining: " + str(self.remaining) + ", isdone: " + str(self.isdone) + "}";



class  ScannerState(Enum):
        IDLE = 1 
        WAITING_FOR_HEADER = 2
        WAITING_FOR_EXT_TYPE = 3
        WAITING_FOR_LENGTH = 4
        WAITING_FOR_VALUE = 5
        SEGMENT_ENDED = 6
        
    

class   ExtTypeParser():
    __metaclass__ = ABCMeta
    
        
    @abstractmethod
    def deserializer(self, exttype, data):
        '''
            Should be implemented for every user defined extension type
        :param data:
        '''
        
        
        

class TimestampParser(ExtTypeParser):
    
    def deserialize(self, exttype, data):
        pass
        
        
        
        

    
    

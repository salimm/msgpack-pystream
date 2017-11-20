'''
Created on Nov 13, 2017

@author: Salim
'''
from _pyio import __metaclass__
from abc import ABCMeta, abstractmethod
from enum import Enum
from msgpackstream.format import FormatUtil, SegmentType, FormatType, ValueType, \
    EventType
from msgpackstream.errors import InvalidStateException
from _io import BytesIO
import binascii
import struct



class StreamUnpacker():
    '''
        StreamUnpacker provides a SAX-like unpacker that reads the input in stream and in batches. It will generate events accordingly. 
    '''
    
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
        '''
            Process the input buffer. The buffer can contains all or a segment of the bytes from the complete message. 
            The function will buffer what will require extra bytes to be processed. 
        :param buff:
        '''
        
        # prepare pointers and inputs
        idx = self.memory.tell()
        self.memory.write(buff)
        self.memory.seek(idx)
                
        # read first byte 
        byte = self.memory.read(1)
        
        # process input while exists
        while byte:
#             print(str(self.lastidx) + ' - ' + str(idx))
#             print(self._scstate)
#             print(self._state)
            byte = ord(byte)
            
            # expected start of a new segment
            if self._scstate in [ScannerState.IDLE, ScannerState.WAITING_FOR_HEADER]:                
                self.handle_read_header(byte)
                self.lastidx = idx + 1
            # the scanner expects to read one or multiple bytes that contain an 
            # integer contain the length of the value to be expected
            elif self._scstate is ScannerState.WAITING_FOR_LENGTH:
                self._state.remaining -= 1;  # decrease number of remaining bytes to get length
                if(self._state.remaining == 0):  # if no more bytes remaining
                    self.handle_read_length(self.memory, self.lastidx, idx + 1)
                    self.lastidx = idx + 1
            # if the scanner is expecting to parse one or multiple bytes as the value of the segment
            elif self._scstate is ScannerState.WAITING_FOR_VALUE:
                self._state.remaining -= 1;                
                if(self._state.remaining == 0):
                    self.handle_read_value(self.memory, self.lastidx, idx + 1)
                    self.lastidx = idx + 1
            # if the scanner is expecting to parse an extension
            elif self._scstate is ScannerState.WAITING_FOR_EXT_TYPE:
                pass            
            
            # if a data segment is ended
            if self._scstate is ScannerState.SEGMENT_ENDED:
                self.handle_segment_ended()
            # proceed with scanning   
            idx = idx + 1
            byte = self.memory.read(1)
        
        # not finished processing all since it needed extra info     
        if self.lastidx is idx:
            self.memory = BytesIO()
            self.lastidx = 0
                
        
    
    def handle_read_length(self, buff, start, end):        
        '''
            handle read of number bytes needed to parse the value 
        :param buff:
        :param start:
        :param end:
        '''
        self._state.length = self.parse_uint(buff, start, end) * self._state.template.value.multiplier
    
        if self.current_state().template.value.valuetype is ValueType.NESTED:
            self.push_state()
            self._scstate = ScannerState.WAITING_FOR_HEADER
        else:
            self._scstate = ScannerState.WAITING_FOR_VALUE    
        
    
    def handle_read_value(self, buff, start, end):
        '''
            handle read of the value based on the expected length
        :param buff:
        :param start:
        :param end:
        '''
        segmenttype = self._state.template.value.segmenttype
        # parsing value 
        if segmenttype in [SegmentType.HEADER_VALUE_PAIR, SegmentType.VARIABLE_LENGTH_VALUE, SegmentType.HEADER_WITH_LENGTH_VALUE_PAIR]:
            self._scstate = ScannerState.SEGMENT_ENDED
            value = self.parse_value(self._state.formattype, buff, start, end)
            self.events.append((self.prefix, EventType.VALUE, self._state.formattype, value))
        # next we should expect length
        elif segmenttype in [SegmentType.FIXED_EXT_FORMAT, SegmentType.EXT_FORMAT]:
            self.events.append((self.prefix, EventType.EXT, self._state.formattype, buff[start:end]))
        else:
            raise InvalidStateException(self._scstate, "header")
                  
    
    def handle_read_header(self, byte):
        '''
            handle read of header and assign fetching the appropriate template that is needed to parse expected segment based on header
        :param byte:
        '''
        
        frmt = self.util.find(byte)
        template = self.util.find_template(frmt.value.code)
        segmenttype = template.value.segmenttype        
        # single byte segment
        if segmenttype is SegmentType.SINGLE_BYTE:
            self._scstate = ScannerState.SEGMENT_ENDED
            self._state = ParserState(frmt, template, isdone=True);
            self.events.append((self.prefix, EventType.VALUE, frmt, self.util.get_value(byte, frmt)))
        # next we should expect value
        elif segmenttype is SegmentType.HEADER_VALUE_PAIR:
            self._scstate = ScannerState.WAITING_FOR_VALUE
            self._state = ParserState(frmt, template, length=template.value.length * template.value.multiplier , isdone=False);            
        # next we should expect value
        elif segmenttype is SegmentType.HEADER_WITH_LENGTH_VALUE_PAIR:
            self._state = ParserState(frmt, template, length=self.util.get_value(byte, frmt) * template.value.multiplier , isdone=False);
            if self._state.template.value.valuetype is ValueType.NESTED:
                self.events.append((self.prefix, self._state.template.value.startevent, frmt, None))
                self.push_state()
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
        
    def handle_segment_ended(self):
        '''
            process end of the segment based on template
        '''
        if self._state.template.value.endevent is not None:
            self.events.append((self.prefix, self._state.template.value.endevent, self._state.formattype, None))
             
        if(len(self._stack) is  0):
            self._scstate = ScannerState.IDLE            
            return         
        self.pop_state()
        self._state.remaining = self._state.remaining - 1
        if self._state.remaining is 0:
            self._scstate = ScannerState.SEGMENT_ENDED
            self.handle_segment_ended()
        else:
            self._scstate = ScannerState.WAITING_FOR_HEADER
            self.push_state()
        
    
    def push_state(self):
        '''
            push the current state to stack and prepare for new segment to be read 
        '''
        self._stack.append(self._state)
        self._state = None
        
    def pop_state(self):
        '''
            pop what exists from stack
        '''
        self._state = self._stack.pop()        
         
                    
    
    def parse_value(self, formattype, buff, start, end):
        '''
            parse the value from the buffer given the interval for the appropraite bytes
        :param formattype:
        :param buff:
        :param start:
        :param end:
        '''
        if(formattype in [FormatType.STR_16, FormatType.STR_8, FormatType.STR_32, FormatType.FIXSTR]):
            return self.parse_str(buff, start, end)
        elif(formattype in [ FormatType.INT_16, FormatType.INT_32, FormatType.INT_64, FormatType.INT_8, FormatType.UINT_16, FormatType.UINT_32, FormatType.UINT_8, FormatType.UINT_64]):
            return self.parse_int(buff, start, end)
        elif(formattype in [ FormatType.FLOAT_32]):
            return self.parse_float32(buff, start, end)
        elif(formattype in [  FormatType.FLOAT_64]):
            return self.parse_float64(buff, start, end)
    
    def parse_uint(self, buff, start, end):
        '''
            parse an integer from the buffer given the interval of bytes
        :param buff:
        :param start:
        :param end:
        '''
        buff.seek(start)
        return int(binascii.hexlify(buff.read((end - start))), 16)
    
    def parse_int(self, buff, start, end):
        '''
            parse an integer from the buffer given the interval of bytes
        :param buff:
        :param start:
        :param end:
        '''
        num = self.parse_uint(buff, start, end)
        l = (end - start)
        return self.twos_comp(num, l * 8)
    
    def parse_float32(self, buff, start, end):
        buff.seek(start)
        return struct.unpack('>f',buff.read((end - start)))[0]
    
    def parse_float64(self, buff, start, end):
        buff.seek(start)
        return struct.unpack('>d',buff.read((end - start)))[0]
    
    def twos_comp(self, val, bits):
        if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)  # compute negative value
        return val  
    
    def parse_str(self, buff, start, end):
        '''
            parse string from the buffer
            
        :param buff:
        :param start:
        :param end:
        '''
        buff.seek(start)
        return buff.read((end - start)) 
    
    
    def generate_events(self):
        '''
            returns the generated events for the given segment of bytes
        '''
        tmp = self.events
        self.events = []
        return tmp
    
    def current_state(self):
        '''
            returns the current state
        '''
        return self._state
    
    '''
        No set function to prevent other classes to change state
    '''
    state = property(current_state)
    
    

    
class ParserState():
    '''
        Contains state of the parser. Parser state is represented by formattype to be prased, 
        template to be parsed based on and the length needed in the parsing process.
         
    '''
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
    '''
        Scanner state contains the intention of the scanner and what it expects next based on what it has read so far
    '''
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
        
        
        
        

    
    

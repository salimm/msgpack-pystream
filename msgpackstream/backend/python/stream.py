'''
Created on Nov 13, 2017

@author: Salim
'''
from _pyio import __metaclass__
from msgpackstream.backend.python.format import FormatUtil 
from msgpackstream.defs import SegmentType, FormatType, ValueType, EventType, ExtType  ,\
    TimestampParser
import struct
from msgpackstream.errors import InvalidStateException
from enum import Enum



class  ScannerState(Enum):
    '''
        Scanner state contains the intention of the scanner and what it expects next based on what it has read so far
    '''
    IDLE = 1  # parser just started or has processed all given data successfully (no buffer exists)
    WAITING_FOR_HEADER = 2  # expecting a header byte to be read next
    WAITING_FOR_EXT_TYPE = 3  # expecting an extension type segment  
    WAITING_FOR_LENGTH = 4  # expecting length of the value to be read next
    WAITING_FOR_VALUE = 5  # expecting value to be read first
    SEGMENT_ENDED = 6  # segment finished parsing
        

    

    
    



class StreamUnpacker():
    '''
        StreamUnpacker provides a SAX-like unpacker that reads the input in stream and in batches. It will generate events accordingly. 
    '''
    
    def __init__(self):        
        self._stack = []
        self._scstate = ScannerState.IDLE
        self._state = None
        self.util = FormatUtil();
        self._templatelist = self.util._templatelist
        self.events = []
        self.memory = ''
        self._deserializers = {}
        self.register(TimestampParser())
        self._available = 0
#         self.timeheader = 0
#         self.timevalue = 0
#         self.timelength = 0
#         self.timetop = 0
#         self.htime = 0
#         self.timebottom = 0
#         self.timesegend = 0
        self.waitingforprop = 0
        self.parentismap = 0
#         self.timeheaders = [0, 0, 0, 0, 0, 0, 0, 0]
#         self.timevalues = [0, 0, 0, 0, 0, 0, 0, 0]
        self._advance = 1
        self.ustructmap = {1:'>B', 2:'>H', 4:'>L', 8:'>Q'}
        self.structmap = {1:'>b', 2:'>h', 4:'>l', 8:'>q    '}
    
    
    
    
    def process(self, buff):
        '''
            Process the input buffer. The buffer can contains all or a segment of the bytes from the complete message. 
            The function will buffer what will require extra bytes to be processed. 
        :param buff:
        '''
        
        
        
        
        # t1 = time.time()
        # adding the current to the available
        self.memory = self.memory + buff 
        self._available = len(self.memory)
        idx = 0
        # prepare pointers and inputs
        # read first byte 
        
        handleheader = self.handle_read_header
        handlelength = self.handle_read_length
        handlevalue = self.handle_read_value
        handleegend = self.handle_segment_ended
        
#         self.timetop += time.time() - t1
        # process input while exists
        while self._available >= self._advance:
            
            # expected start of a new segment
            if self._scstate.value <= ScannerState.WAITING_FOR_HEADER.value:
                # t1 = time.time()
                self._advance = 1
#                 byte = ord(self.memory[idx])
                handleheader(self.memory[idx])
                # self.timeheader += time.time() - t1
            # the scanner expects to read one or multiple bytes that contain an 
            # integer contain the length of the value to be expected
            elif self._scstate is ScannerState.WAITING_FOR_LENGTH:
                # t1 = time.time()
                self._advance = self._state[3]
                # breaking if not available
                if self._available < self._state[3]:
                    break
                handlelength(self.memory, idx, idx + self._advance)
                # self.timelength += time.time() - t1
                # if the scanner is expecting to parse one or multiple bytes as the value of the segment
            elif self._scstate is ScannerState.WAITING_FOR_VALUE:
                # t1 = time.time()
                self._advance = self._state[3]
                if self._available < self._advance:
                    break
                handlevalue(self.memory, idx, idx + self._advance)
                # self.timevalue += time.time() - t1
            # if the scanner is expecting to parse an extension
            elif self._scstate is ScannerState.WAITING_FOR_EXT_TYPE:
                self._advance = 1
                self.handle_read_ext_type(self.memory, idx)
            
            # if a data segment is ended
            if self._scstate is ScannerState.SEGMENT_ENDED:
                # t1 = time.time() 
                handleegend()
                # self.timesegend += time.time() - t1             
            # proceed with scanning
            
            self._available -= self._advance   
            idx = idx + self._advance
            self._advance = 1
        
        # t1 = time.time()
        #  finished processing all since it needed extra info     
        self.memory = buffer(self.memory, idx, len(self.memory))
        
        # self.timebottom += time.time() - t1
        
        
    
    def handle_read_length(self, buff, start, end):        
        '''
            handle read of number bytes needed to parse the value 
        :param buff:
        :param start:
        :param end:
        '''
        self.set_state_length(self._state, self.parse_uint(buff, start, end) * self._state[1].value.multiplier)
    
        if self._state[1].value.valuetype is ValueType.NESTED:
            self.events.append((self._state[1].value.startevent, self._state[0], None))
            if self._state[2] is 0:  # it is an empty nested segment
                self._scstate = ScannerState.SEGMENT_ENDED
            else:
                if self._state[1].value.multiplier is 2:
                    self.parentismap = 1
                    self.waitingforprop = 1
                else:
                    self.parentismap = 0
                    self.waitingforprop = 0
                    
                self.push_state()
                self._scstate = ScannerState.WAITING_FOR_HEADER
        else:
            if self._state[1].value.segmenttype is SegmentType.EXT_FORMAT:
                self._scstate = ScannerState.WAITING_FOR_EXT_TYPE
            else:
                self._scstate = ScannerState.WAITING_FOR_VALUE
                if self._state[2] is 0:  # it is an empty nested segment
                    self.events.append((self.value_event_type(EventType.VALUE), self._state[0], self.empty_value(self._state[0])))
                    self._scstate = self.next_state_afterraw()
                    self._scstate = ScannerState.SEGMENT_ENDED
                
        
    
    def handle_read_value(self, buff, start, end):
        '''
            handle read of the value based on the expected length
        :param buff:
        :param start:
        :param end:
        '''
        # t1 = time.time()
        segmenttype = self._state[1].value.segmenttype
        
        value = None
        eventtype = None
        ftype = self._state[0]
        # self.timevalues[0] += time.time() -t1
        # parsing value 
        if segmenttype <= SegmentType.VARIABLE_LENGTH_VALUE:
            # t1 = time.time()
            self._scstate = self.next_state_afterraw()
#             self._scstate = ScannerState.SEGMENT_ENDED
            value = self.parse_value(self._state[0], buff, start, end)
            eventtype = EventType.VALUE 
            # self.timevalues[1] += time.time() -t1
        # next we should expect length
        elif segmenttype >= SegmentType.EXT_FORMAT:
            # t1 = time.time() 
            value = self.parse_ext_value(self._state[0], self._state[4], buff, start, end)
            eventtype = EventType.EXT
            ftype = ExtType(self._state[0], self._state[4])
            # self.timevalues[2] += time.time() -t1
        else:
            raise InvalidStateException(self._scstate, "header")
        # t1 = time.time()
        self.events.append((self.value_event_type(eventtype), ftype, value))
        # self.timevalues[3] += time.time() -t1
    
    def handle_read_header(self, byte):
        '''
            handle read of header and assign fetching the appropriate template that is needed to parse expected segment based on header
        :param byte:
        '''
        
        # t1 = time.time()
        (_, frmtcode, _, frmtidx, val) = self.util.find(byte)
        # self.timeheaders[0] += time.time() - t1
        # t1 = time.time()
        template = self._templatelist[frmtidx - 1]
        # self.timeheaders[1] += time.time() - t1
        
        segmenttype = template.value.segmenttype        
        # single byte segment
       
        if segmenttype is SegmentType.SINGLE_BYTE:
            # t1 = time.time()
            self._scstate = self.next_state_afterraw()
#             self._scstate = ScannerState.SEGMENT_ENDED
            self._state = self.create_state(frmtcode, template);
#             self.events.append((self.value_event_type(EventType.VALUE), frmt, self.util.get_value(byte, frmt)))
            self.events.append((self.value_event_type(EventType.VALUE), frmtcode, val))
            # self.timeheaders[2] += time.time() - t1
            
        # next we should expect value
        elif segmenttype is SegmentType.HEADER_VALUE_PAIR:
            # t1 = time.time()
            self._scstate = ScannerState.WAITING_FOR_VALUE
            self._state = self.create_state(frmtcode, template, length=template.value.length * template.value.multiplier);
            # self.timeheaders[3] += time.time() - t1            
        # next we should expect value
        elif segmenttype is SegmentType.HEADER_WITH_LENGTH_VALUE_PAIR:
            # t1 = time.time()
            length = val * template.value.multiplier
#             length = self.util.get_value(byte, frmt) * template.value.multiplier
            self._state = self.create_state(frmtcode, template, length=length);
            if self._state[1].value.valuetype is ValueType.NESTED:                
                self.events.append((self._state[1].value.startevent, frmtcode, None))
                if length is 0:
                    self._scstate = ScannerState.SEGMENT_ENDED
                else:
                    if template.value.multiplier is 2:
                        self.parentismap = 1
                        self.waitingforprop = 1
                    else:
                        self.parentismap = 0
                        self.waitingforprop = 0
                    self.push_state()
                    self._scstate = ScannerState.WAITING_FOR_HEADER
            else:          
                if length is 0:
                    self.events.append((self.value_event_type(EventType.VALUE), self._state[0], self.empty_value(self._state[0])))
                    self._scstate = self.next_state_afterraw()
#                     self._scstate = ScannerState.SEGMENT_ENDED
                else:
                    self._scstate = ScannerState.WAITING_FOR_VALUE
            # self.timeheaders[4] += time.time() - t1
        # next we should expect length
        elif segmenttype is SegmentType.VARIABLE_LENGTH_VALUE:
            # t1 = time.time()
            self._scstate = ScannerState.WAITING_FOR_LENGTH
            self._state = self.create_state(frmtcode, template, length=template.value.length);
            # self.timeheaders[5] += time.time() - t1
        # next we should expect length
        elif segmenttype is SegmentType.EXT_FORMAT:
            # t1 = time.time()
            self._scstate = ScannerState.WAITING_FOR_LENGTH
            self._state = self.create_state(frmtcode, template, length=template.value.length);
            # self.timeheaders[6] += time.time() - t1
        # next we should expect type       
        elif segmenttype is SegmentType.FIXED_EXT_FORMAT:
            # t1 = time.time()
            self._state = self.create_state(frmtcode, template, length=template.value.length);
            self._scstate = ScannerState.WAITING_FOR_EXT_TYPE
            # self.timeheaders[7] += time.time() - t1
        else:
            raise InvalidStateException(self._scstate, "header")
        
    def handle_read_ext_type(self, buff, idx):
        extcode = self.parse_int(buff, idx, idx + 1)
        self._state[4] = extcode
        self._scstate = ScannerState.WAITING_FOR_VALUE
        if self._state[2] is 0:  # it is an empty nested segment
            self.events.append((EventType.EXT, ExtType(self._state[0], self._state[4]), b''))
            self._scstate = self.next_state_afterraw()
#             self._scstate = ScannerState.SEGMENT_ENDED
    
    
    def value_event_type(self, eventtype):
        etype = None 
        if self.waitingforprop == 1:
            etype = EventType.MAP_PROPERTY_NAME
        else:
            etype = eventtype
        if self.parentismap == 1:
            self.waitingforprop = 1 - self.waitingforprop
        return etype
            
               
        
        
    def parse_ext_value(self, formattype, extcode, buff, start, end):
        parser = self._deserializers.get(extcode, None)
        if parser:
            return parser.deserialize(ExtType(formattype, extcode), buff, start , end)
        else:
            return buff[start: end]
      
    def handle_segment_ended(self):
        '''
            process end of the segment based on template
        '''
        if self._state[1].value.endevent is not None:
            self.events.append((self._state[1].value.endevent, self._state[0], None))
            
        if self._state[1].value.multiplier is 2:
            self.parentismap = 0
            self.waitingforprop = 0
             
        if(len(self._stack) is  0):
            self._scstate = ScannerState.IDLE            
            return       
        
        if self._state[1].value.valuetype is not ValueType.RAW:
            self._stack[-1][3] = self._stack[-1][3] - 1  # #???
            
        if self._stack[-1][3] is 0:
            self._scstate = ScannerState.SEGMENT_ENDED
            self._state = self._stack.pop()  # pop last state from stack
            if self._state[1].value.multiplier is 2:
                self.parentismap = 1
                self.waitingforprop = 1
                   
            self.handle_segment_ended()
        else:
            if self._stack[-1][1].value.multiplier is 2:
                self.parentismap = 1
                self.waitingforprop = 1
            self._scstate = ScannerState.WAITING_FOR_HEADER
        
    
    def next_state_afterraw(self):
        try:
            self._stack[-1][3] = self._stack[-1][3] - 1  # #???
            if self._stack[-1][3] == 0:
                return ScannerState.SEGMENT_ENDED
            else:
                return  ScannerState.WAITING_FOR_HEADER
        except:
            return  ScannerState.WAITING_FOR_HEADER
            
    
    
    def push_state(self):
        '''
            push the current state to stack and prepare for new segment to be read 
        '''
        self._stack.append(self._state)
        self._state = None
      
        
                    
    def empty_value(self, frmtcode):
        return self.util.emptyvals[frmtcode]
    
    
    def parse_value(self, frmtcode, buff, start, end):
        '''
            parse the value from the buffer given the interval for the appropraite bytes
        :param formattype:
        :param buff:
        :param start:
        :param end:
        '''
        
        frmttype = self.util._formatmap[frmtcode]
        if(frmtcode == FormatType.FLOAT_32.value.code):  # @UndefinedVariable
            return self.parse_float32(buff, start, end)
        elif(frmtcode == FormatType.FLOAT_64.value.code):  # @UndefinedVariable
            return self.parse_float64(buff, start, end)
        if frmttype.value.idx <= FormatType.FIXSTR.value.idx:  # @UndefinedVariable  
            return self.parse_str(buff, start, end)
        elif frmttype.value.idx <= FormatType.INT_64.value.idx:  # @UndefinedVariable
            return self.parse_int(buff, start, end)
        elif frmttype.value.idx <= FormatType.UINT_64.value.idx:  # @UndefinedVariable
            return self.parse_uint(buff, start, end)
    
    def parse_uint(self, buff, start, end):
        '''
            parse an integer from the buffer given the interval of bytes
        :param buff:
        :param start:
        :param end:
        
        '''
        return struct.unpack_from(self.ustructmap[end - start], buff, start)[0]
    
    def parse_int(self, buff, start, end):
        '''
            parse an integer from the buffer given the interval of bytes
        :param buff:
        :param start:
        :param end:
        '''
#         num = self.parse_uint(buff, start, end)
#         l = (end - start)
#         return self.twos_comp(num, l * 8)
        return struct.unpack_from(self.structmap[end - start], buff, start)[0]
    
    def parse_float32(self, buff, start, end):
        '''
            parses float 32 bit
        :param buff:
        :param start:
        :param end:
        '''
        return struct.unpack_from('>f', buff, start)[0]
    
    def parse_float64(self, buff, start, end):
        '''
            parses float 64 bit
        :param buff:
        :param start:
        :param end:
        '''
        return struct.unpack_from('>d', buff, start)[0]
    
    def twos_comp(self, val, bits):
        '''
            two complement to get negative
        :param val:
        :param bits:
        '''
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
        return buff[start:end]
    
    def parse_bin(self, buff, start, end):
        '''
            parse binary array
            
        :param buff:
        :param start:
        :param end:
        '''
        return buff[start:end]
    
    
    def generate_events(self):
        '''
            returns the generated events for the given segment of bytes
        '''
        tmp = self.events
        self.events = []
        return tmp
    

    def register(self, parser):
        self._deserializers[parser.handled_extcode()] = parser
    
    
    def create_state(self, formattype, template, length=None, extcode=None):
        return [formattype, template, length, length, extcode]
    
    def set_state_length(self, state, length):
        state[2] = length
        state[3] = length
    
    

        

 
def unpack(instream, buffersize=4000, parsers=[]):
    '''
        Creates an iterator instance for the unpacker
    :param instream:
    :param buffersize:
    '''
    return UnpackerIterator(instream, buffersize, parsers)
    
    
    
    
class UnpackerIterator(object):
    
    def __init__(self, instream, buffersize=5000, parsers=[]):
        self._instream = instream
        self._unpacker = StreamUnpacker()
        for parser in parsers:
            self._unpacker.register(parser)
        self._buffersize = buffersize
        self._events = []
        self._idx = 0
        #self.time = 0
        #self.ptime = 0
        
    
    def __iter__(self):
        return self

    def __next__(self):
        if self._idx >= len(self._events):
#             #t1 = time.time()
            self._events = []
            while len(self._events) is 0:
                self._idx = 0
                bytes_read = self._instream.read(self._buffersize)
                if not bytes_read:
#                     print("header: " + str(self._unpacker.timeheader) + "length: " + str(self._unpacker.timelength) + " value: " + str(self._unpacker.timevalue) + "  top: " + str(self._unpacker.timetop) + "  bottom: " + str(self._unpacker.timebottom) + "  htime: " + str(self._unpacker.htime) + "  time segend: " + str(self._unpacker.timesegend))
#                     print("headers: " + str(self._unpacker.timeheaders))
#                     print("values: " + str(self._unpacker.timevalue))
#                     print("total time: " + str(#self.time))
#                     print("total p time: " + str(self.ptime))
#                     print("total time: " + str(self.time))
                    raise StopIteration()
#                 t11 = time.time()
                self._unpacker.process(bytes_read)
                self._events = self._unpacker.generate_events()
                #self.ptime += time.time() - t11
#             self.time += time.time() - t1
        event = self._events[self._idx]
        self._idx = self._idx + 1 
        return event
        
        

    next = __next__  # Python 2   



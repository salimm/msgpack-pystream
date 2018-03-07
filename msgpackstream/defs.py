'''
Created on Nov 13, 2017

@author: Salim
'''
from enum import Enum
from abc import ABCMeta, abstractmethod
import struct
import datetime


class Format():
    
    def __init__(self, idx, code, mask):
        self.idx = idx
        self.code = code
        self.mask = mask
        
        
    def __str__(self):
        return "{ idx: " + str(self.id) + " code: " + str(self.code) + ", mask: " + str(self.mask) + " }"


class FormatType(Enum):
    
    POS_FIXINT = Format(36, 0x00 , 0x80)
    NEG_FIXINT = Format(37, 0xE0 , 0xE0)
    
    FIXMAP = Format(21, 0x80 , 0xF0)
    FIXARRAY = Format(20, 0x90 , 0xF0)
    FIXSTR = Format(7, 0xA0 , 0xE0)
    
    NIL = Format(34, 0xC0 , 0xFF)
    NEVER_USED = Format(35, 0xC1 , 0xFF)
    
    FALSE = Format(32, 0xC2 , 0xFF)
    TRUE = Format(33, 0xC3 , 0xFF)
    
    BIN_8 = Format(1, 0xC4 , 0xFF)
    BIN_16 = Format(2, 0xC5 , 0xFF)
    BIN_32 = Format(3, 0xC6 , 0xFF)
    
    EXT_8 = Format(29, 0xC7 , 0xFF)
    EXT_16 = Format(30, 0xC8 , 0xFF)
    EXT_32 = Format(31, 0xC9 , 0xFF)
    
    
    FLOAT_32 = Format(16, 0xCA , 0xFF)
    FLOAT_64 = Format(17, 0xCB , 0xFF)
    
    UINT_8 = Format(12, 0xCC , 0xFF)
    UINT_16 = Format(13, 0xCD , 0xFF)
    UINT_32 = Format(14, 0xCE , 0xFF)
    UINT_64 = Format(15, 0xCF , 0xFF)
    
    INT_8 = Format(8, 0xD0 , 0xFF)
    INT_16 = Format(9, 0xD1 , 0xFF)
    INT_32 = Format(10, 0xD2 , 0xFF)
    INT_64 = Format(11, 0xD3 , 0xFF)
    
    FIXEXT_1 = Format(24, 0xD4 , 0xFF)
    FIXEXT_2 = Format(25, 0xD5 , 0xFF)
    FIXEXT_4 = Format(26, 0xD6 , 0xFF)
    FIXEXT_8 = Format(27, 0xD7 , 0xFF)
    FIXEXT_16 = Format(28, 0xD8 , 0xFF)
    
    STR_8 = Format(4, 0xD9 , 0xFF)
    STR_16 = Format(5, 0xDA , 0xFF)
    STR_32 = Format(6, 0xDB , 0xFF)
    
    ARRAY_16 = Format(18, 0xDC , 0xFF)
    ARRAY_32 = Format(19, 0xDD , 0xFF)
    
    MAP_16 = Format(22, 0xDE , 0xFF)
    MAP_32 = Format(23, 0xDF , 0xFF)
    
       
    
class SegmentType():
    
    HEADER_VALUE_PAIR = 1  # one header and multiple bytes for value
    HEADER_WITH_LENGTH_VALUE_PAIR = 2  # one header, it also includes length of value paired with value which of variable length
    VARIABLE_LENGTH_VALUE = 3  # 1 byte for header, multiple bytes for number of items, items
    
    SINGLE_BYTE = 4  # head contain value
    
    
    EXT_FORMAT = 5
    FIXED_EXT_FORMAT = 6
    

class ValueType(Enum):
    RAW = 1
    NESTED = 2
    NONE = 3
    

class Template():
    
    def __init__(self, formattype, segmenttype, valuetype, startevent, endevent, length, multiplier):
        self.formattype = formattype
        self.segmenttype = segmenttype        
        self.valuetype = valuetype
        self.startevent = startevent
        self.endevent = endevent        
        self.length = length
        self.multiplier = multiplier
        
        
        
    def __str__(self):
        return "{ format:" + str(self.formattype) + ", segment: " + str(self.segmenttype) + ", length: " + str(self.length) + ", multiplier: " + str(self.multiplier) + ", valuetype:" + str(self.valuetype) + ", startevent:" + str(self.startevent) + ", endevent:" + str(self.endevent) + "}"
    
        

class EventType(Enum):
    
    VALUE = 1  # value event
    ARRAY_START = 2  # event that indicates start of an array
    ARRAY_END = 3  # event that indicates end of an array
    MAP_START = 4  # event that indicates start of a map
    MAP_END = 5  # event that indicates end of a map
    MAP_PROPERTY_NAME = 6  # event that indicates property name
    EXT = 7  # event that indicates ext value
              
    
class TemplateType(Enum):
    '''
    SegmentTemplate is an enum containing information required to parse segment. Each segement type contains an array of values with the following items:
        [FormatType, SegmentType, #value_bytes/#value_length_bytes, multiplier_of_length/#parts_per_item]
    '''
    POS_FIXINT = Template(FormatType.POS_FIXINT, SegmentType.SINGLE_BYTE, ValueType.RAW, None, None, 0, 1)
    NEG_FIXINT = Template(FormatType.NEG_FIXINT, SegmentType.SINGLE_BYTE, ValueType.RAW, None, None, 0, 1)
    
    FIXMAP = Template(FormatType.FIXMAP, SegmentType.HEADER_WITH_LENGTH_VALUE_PAIR, ValueType.NESTED, EventType.MAP_START, EventType.MAP_END, 0, 2)
    FIXARRAY = Template(FormatType.FIXARRAY, SegmentType.HEADER_WITH_LENGTH_VALUE_PAIR, ValueType.NESTED, EventType.ARRAY_START, EventType.ARRAY_END, 0, 1)
    FIXSTR = Template(FormatType.FIXSTR, SegmentType.HEADER_WITH_LENGTH_VALUE_PAIR, ValueType.RAW, None, None, 0, 1)
    
    NIL = Template(FormatType.NIL , SegmentType.SINGLE_BYTE, ValueType.NONE, None, None, 0, 1)
    NEVER_USED = Template(FormatType.NEVER_USED, SegmentType.SINGLE_BYTE, ValueType.NONE, None, None, 0, 1)
    
    FALSE = Template(FormatType.FALSE , SegmentType.SINGLE_BYTE, ValueType.RAW, None, None, 0, 1)
    TRUE = Template(FormatType.TRUE, SegmentType.SINGLE_BYTE, ValueType.RAW, None, None, 0, 1)
    
    BIN_8 = Template(FormatType.BIN_8, SegmentType.VARIABLE_LENGTH_VALUE, ValueType.RAW, None, None, 1, 1)
    BIN_16 = Template(FormatType.BIN_16, SegmentType.VARIABLE_LENGTH_VALUE, ValueType.RAW, None, None, 2, 1)
    BIN_32 = Template(FormatType.BIN_32, SegmentType.VARIABLE_LENGTH_VALUE, ValueType.RAW, None, None, 4, 1)
    
    EXT_8 = Template(FormatType.EXT_8, SegmentType.EXT_FORMAT, ValueType.RAW, None, None, 1, 1)
    EXT_16 = Template(FormatType.EXT_16, SegmentType.EXT_FORMAT, ValueType.RAW, None, None, 2, 1)
    EXT_32 = Template(FormatType.EXT_32, SegmentType.EXT_FORMAT, ValueType.RAW, None, None, 4, 1)
    
    
    FLOAT_32 = Template(FormatType.FLOAT_32, SegmentType.HEADER_VALUE_PAIR, ValueType.RAW, None, None, 4, 1)
    FLOAT_64 = Template(FormatType.FLOAT_64, SegmentType.HEADER_VALUE_PAIR, ValueType.RAW, None, None, 8, 1)
    
    UINT_8 = Template(FormatType.UINT_8, SegmentType.HEADER_VALUE_PAIR, ValueType.RAW, None, None, 1, 1)
    UINT_16 = Template(FormatType.UINT_16, SegmentType.HEADER_VALUE_PAIR, ValueType.RAW, None, None, 2, 1)
    UINT_32 = Template(FormatType.UINT_32, SegmentType.HEADER_VALUE_PAIR, ValueType.RAW, None, None, 4, 1)
    UINT_64 = Template(FormatType.UINT_64, SegmentType.HEADER_VALUE_PAIR, ValueType.RAW, None, None, 8, 1)
    
    INT_8 = Template(FormatType.INT_8, SegmentType.HEADER_VALUE_PAIR, ValueType.RAW, None, None, 1, 1)
    INT_16 = Template(FormatType.INT_16, SegmentType.HEADER_VALUE_PAIR, ValueType.RAW, None, None, 2, 1)
    INT_32 = Template(FormatType.INT_32, SegmentType.HEADER_VALUE_PAIR, ValueType.RAW, None, None, 4, 1)
    INT_64 = Template(FormatType.INT_64, SegmentType.HEADER_VALUE_PAIR, ValueType.RAW, None, None, 8, 1)
    
    FIXEXT_1 = Template(FormatType.FIXEXT_1, SegmentType.FIXED_EXT_FORMAT, ValueType.RAW, None, None, 1, 1)
    FIXEXT_2 = Template(FormatType.FIXEXT_2, SegmentType.FIXED_EXT_FORMAT, ValueType.RAW, None, None, 2, 1)
    FIXEXT_4 = Template(FormatType.FIXEXT_4, SegmentType.FIXED_EXT_FORMAT, ValueType.RAW, None, None, 4, 1)
    FIXEXT_8 = Template(FormatType.FIXEXT_8, SegmentType.FIXED_EXT_FORMAT, ValueType.RAW, None, None, 8, 1)
    FIXEXT_16 = Template(FormatType.FIXEXT_16, SegmentType.FIXED_EXT_FORMAT, ValueType.RAW, None, None, 16, 1)
    
    STR_8 = Template(FormatType.STR_8, SegmentType.VARIABLE_LENGTH_VALUE, ValueType.RAW, None, None, 1, 1)
    STR_16 = Template(FormatType.STR_16, SegmentType.VARIABLE_LENGTH_VALUE, ValueType.RAW, None, None, 2, 1)
    STR_32 = Template(FormatType.STR_32, SegmentType.VARIABLE_LENGTH_VALUE, ValueType.RAW, None, None, 4, 1)
    
    ARRAY_16 = Template(FormatType.ARRAY_16, SegmentType.VARIABLE_LENGTH_VALUE, ValueType.NESTED, EventType.ARRAY_START, EventType.ARRAY_END, 2, 1)
    ARRAY_32 = Template(FormatType.ARRAY_32, SegmentType.VARIABLE_LENGTH_VALUE, ValueType.NESTED, EventType.ARRAY_START, EventType.ARRAY_END, 4, 1)
    
    MAP_16 = Template(FormatType.MAP_16, SegmentType.VARIABLE_LENGTH_VALUE, ValueType.NESTED, EventType.MAP_START, EventType.MAP_END, 2, 2)
    MAP_32 = Template(FormatType.MAP_32, SegmentType.VARIABLE_LENGTH_VALUE, ValueType.NESTED, EventType.MAP_START, EventType.MAP_END, 4, 2)
    


            
    
class ExtType():
    '''
    Class for Extention Type including format type, template and length in the header
    '''
    __classmeta__ = ABCMeta
    
    def __init__(self, formattype, extcode):
        self._formattype = formattype
        self._extcode = extcode
        
    def get_formattype(self):
        return self._formattype
    
    def set_formattype(self, formattype):
        self._formattype = formattype
        
        
    def get_extcode(self):
        return self._extcode
    
    def set_extcode(self, extcode):
        self._extcode = extcode
    
    formattype = property(get_formattype, set_formattype)
    extcode = property(get_extcode, set_extcode)
    
    def __eq__(self, o):
        if isinstance(o, ExtType):
            return o.extcode == self.extcode and o.formattype == self.formattype
        return False
    
    def __str__(self):
        return "{ format:" + str(self.formattype) + ", extcode:" + str(self._extcode) + "}";
                
        
    
class TimestampType(ExtType):

    def __init__(self, formattype, extcode, length=None):
        
        if(formattype == FormatType.FIXEXT_4):
            length = 32
        elif(formattype == FormatType.FIXEXT_8):
            length = 64
        else:
            length = 96
        ExtType.__init__(self, formattype, extcode, length)
        
            
        
                            
                            
class ParserState():
    '''
        Contains state of the parser. Parser state is represented by formattype to be prased, 
        template to be parsed based on and the length needed in the parsing process.
         
    '''
    def __init__(self, formattype, template, length=None, isdone=False, extcode=None):
        self.formattype = formattype
        self.template = template
        self.remaining = length 
        self.isdone = isdone
        self.extcode = extcode
        
        
    
    def __str__(self):
        return "ParserState formattype: " + str(self.formattype) + ", tempalte: " + str(self.template) + ", length: " + str(self.length) + ", remaining: " + str(self.remaining) + ", isdone: " + str(self.isdone) + ", extcode: " + str(self.extcode) + "}";




class   ExtTypeParser():
    __metaclass__ = ABCMeta
    
        
    @abstractmethod
    def deserialize(self, exttype, buff, start , end):
        '''
            Should be implemented for every user defined extension type
        :param data:
        '''
    @abstractmethod
    def handled_extcode(self):
        pass
        
        
        

class TimestampParser(ExtTypeParser):
    
    def __init__(self):
        self.ustructmap = {1:'>B', 2:'>H', 4:'>L', 8:'>Q'}
        self.structmap = {1:'>b', 2:'>h', 4:'>l', 8:'>q    '}   
    
    def deserialize(self, exttype, buff, start, end):
        if exttype.formattype is FormatType.FIXEXT_4.value.code:  # @UndefinedVariable
            return datetime.datetime.fromtimestamp(self.parse_uint(buff, start, end))
        elif exttype.formattype is FormatType.FIXEXT_8.value.code:  # @UndefinedVariable
            val = self.parse_uint(buff, start, end)
            nsec = val >> 34
            sec = val & 0x00000003ffffffffL
            return datetime.datetime.fromtimestamp(sec + nsec / 1e9)
        elif exttype.formattype is FormatType.EXT_8.value.code:  # @UndefinedVariable
            nsec = self.parse_uint(buff, start, start + 4)
            sec = self.parse_int(buff, start + 4, end)
            return datetime.datetime.fromtimestamp(sec + nsec / 1e9)
        else:
            raise Exception("Unsupported FormatType " + str(exttype.formattype) + " for Timestamp (extcode = -1)!!")        

    
    def handled_extcode(self):
        return -1
    
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
    
    def twos_comp(self, val, bits):
        '''
            two complement to get negative
        :param val:
        :param bits:
        '''
        if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)  # compute negative value
        return val      



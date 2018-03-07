'''
Created on Nov 13, 2017

@author: Salim
'''
from msgpackstream.defs import FormatType, TemplateType




                    
                    
class FormatUtil():
    
    
    def __init__(self):
        self._typelist = list(FormatType)
        self._templatemap = {}
        templist = list(TemplateType)
        for t in templist:
            self._templatemap[t.value.formattype.value.code] = t
        
        self._templatelist = templist
        self._templatelist = sorted(self._templatelist, key=lambda tmp: tmp.value.formattype.value.idx)
        
        self._formatmap = {}
        templist = list(FormatType)
        for t in templist:
            self._formatmap[t.value.code] = t
            
        self._formatlist = templist        
        self._formatlist = sorted(self._formatlist, key=lambda frmt: frmt.value.idx)
        
        self.emptyvals = {}
        for t in templist:
            self.emptyvals[t.value.code] = self._empty_value(t);
            
            
        self._formatlookup  =[]
        for c in range(0,0xFF+1):
            self._formatlookup.append( self.find_slow(c))
            
        
    
    
    def match(self, val, ftype):
        return (val & ftype.value.mask) == ftype.value.code
    
    
    def get_value(self, code, ftype):
        if(ftype is FormatType.NIL):
            return None
        if(ftype is FormatType.FALSE):
            return False
        if(ftype is FormatType.TRUE):
            return True        
        if(ftype is FormatType.NEG_FIXINT):
            return self.twos_comp(code & ~ftype.value.mask, 5)
        return code & ~ftype.value.mask
     
    def find_slow(self, code):
        if  code <= 0x7F:
            return FormatType.POS_FIXINT;
        elif code <= 0x8F:
            return  FormatType.FIXMAP;
        elif code <= 0x9F:
            return  FormatType.FIXARRAY;
        elif code <= 0xBF:
            return FormatType.FIXSTR;
        elif code >= 0xE0:
            return FormatType.NEG_FIXINT;
        else:
            return self._formatmap[code];
        
    def find_fast(self, code):
        code = ord(code)
        frmt = self._formatlookup[code]
        return (frmt, frmt.value.code, frmt.value.mask,frmt.value.idx, self.get_value(code, frmt))
    
    
#     def find_c(self, code):
#         (frmtcode, frmtmask, frmtidx,val) = msgpackfinder.parse_format_code((code))
#         return  (self._formatmap[frmtcode], frmtcode, frmtmask, frmtidx,val)
#     
#     def find_c_fast(self, code):
#         (frmtcode, frmtmask, frmtidx,val) = msgpackfinder.parse_format_code((code))
#         return  (self._formatmap[frmtcode], frmtcode, frmtmask, frmtidx,val)
        
    def find(self, code):
        
        return self.find_fast(code)
        
            
    def _empty_value(self, formattype):
        '''
            returns default empty value 
        :param formattype:
        :param buff:
        :param start:
        :param end:
        '''
        if formattype.value.idx <= FormatType.BIN_32.value.idx:  # @UndefinedVariable
            return b''
        elif formattype.value.idx <= FormatType.FIXSTR.value.idx:  # @UndefinedVariable  
            return ''
        elif formattype.value.idx <= FormatType.INT_64.value.idx:  # @UndefinedVariable
            return 0
        elif formattype.value.idx <= FormatType.UINT_64.value.idx:  # @UndefinedVariable
            return 0
        elif(formattype is FormatType.FLOAT_32):
            return float(0)
        elif(formattype is FormatType.FLOAT_64):
            return float(0)
    
    
    def find_template(self, frmtidx):
        return self._templatelist[frmtidx - 1]
    
    def twos_comp(self, val, bits):
        if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)  # compute negative value
        return val  
            
            
            
            

    
    

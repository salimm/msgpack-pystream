#include <iostream>
#include "HeaderUtil.h"
#include <iostream>


HeaderUtil::HeaderUtil(){
	// this->frmtlookup = this->create_format_lookup();
    this->create_format_lookup();
	// this->templatelookup = this->create_template_lookup();
    this->create_template_lookup();

    this->create_fval_lookup();
}



   // find the format for code
Format& HeaderUtil::find_format(unsigned char code){
	return this->frmtlookup.at(int(code));
}

// find the format for code
Template& HeaderUtil::find_template(const struct Format &frmt){
	return this->templatelookup[frmt.idx+2];
}

// find the format for code
Template& HeaderUtil::find_template(unsigned char code){
	return this->templatelookup[this->find_format(code).idx+2];
}


// creates lookup table  for format
void HeaderUtil::create_format_lookup(){
	 
    
    for(int i=0; i< 0xFF+1;i++){
        this->frmtlookup.push_back(this->decode_format_code(i));
    }

}

// creates lookup table for template
void HeaderUtil::create_template_lookup(){
    
    for(int i=-2; i< 38;i++){        
        this->templatelookup.push_back(this->decode_template_idx(i));
    }
    
}
	

const int twos_comp(int val, int bits){
    // std::cout << val;
    // std::cout << bits;
    // if ((val & (1<<(bits-1))) !=0){
        return val - (1<<bits);
    // }
    // return val;
}


// extracts value from header byte 
PyObject*  HeaderUtil::get_value(unsigned char header, const struct Format &frmt){
	// std::cout <<"*** hu *** 1\n";
	// std::cout << std::to_string(frmt.idx) +"\n";
	// std::cout << std::to_string(frmt.codexc);
	// std::cout <<"*** hu *** 1.5\n";
	 if (frmt.code == NIL.code){
        Py_INCREF(Py_None);
        return Py_None;
    	
    }else if(frmt.code == TRUE_FORMAT.code){
        Py_INCREF(Py_True);
        return Py_BuildValue("O", Py_True);
    }else if(frmt.code == FALSE_FORMAT.code){
        Py_INCREF(Py_False);
        return Py_BuildValue("O", Py_False);
    }else if(frmt.code == NEG_FIXINT.code){    		
        return Py_BuildValue("i", twos_comp(header & ~frmt.mask,5));        
    }
    else{
    	// std::cout <<"*** hu *** 2\n";
    	int val = int(header & ~frmt.mask);
    	return Py_BuildValue("i", val);
    }
    // return this->fval_lookup[frmt.idx](header,frmt);
    // std::cout <<"*** hu *** 4\n";
}

	


PyObject*  nil_value(unsigned char header,const struct Format &frmt){
    Py_INCREF(Py_None);
    return Py_None;        
}

PyObject*  true_value(unsigned char header,const struct Format &frmt){
    Py_INCREF(Py_True);
    return Py_BuildValue("O", Py_True);
}

PyObject*  false_value(unsigned char header,const struct Format &frmt){
    Py_INCREF(Py_False);
    return Py_BuildValue("O", Py_False);
}

PyObject*  neg_value(unsigned char header,const struct Format &frmt){
    return Py_BuildValue("i", twos_comp(header & ~frmt.mask,5));
}

PyObject*  pos_value(unsigned char header,const struct Format &frmt){
    int val = int(header & ~frmt.mask);
    return Py_BuildValue("i", val);    
}

// creates lookup table for template
void HeaderUtil::create_fval_lookup(){
    
    for(int i=-2; i< 38;i++){        
        if(i==NIL.idx){
            this->fval_lookup.push_back(nil_value);
        }else if (i==TRUE_FORMAT.idx){
            this->fval_lookup.push_back(true_value);
        }else if (i==FALSE_FORMAT.idx){
            this->fval_lookup.push_back(false_value);
        }else if (i==NEG_FIXINT.idx){
            this->fval_lookup.push_back(neg_value);
        }else if (i==POS_FIXINT.idx){
            this->fval_lookup.push_back(pos_value);
        }else {
            this->fval_lookup.push_back(nil_value);
        }
    }
    
}
int  HeaderUtil::get_int_value(unsigned char byte,const struct  Format &frmt){
	if(frmt.code == NEG_FIXINT.code){
        return twos_comp(byte & ~frmt.mask,5);
   }else{
    	return int(byte & ~frmt.mask);
		
   }

}

 PyObject*  HeaderUtil::empty_value(const struct Format &frmt ){

	if (frmt.idx <= BIN_32.idx){	  
	   return Py_BuildValue("s", "");
	}else if (frmt.idx <= FIXSTR.idx){
	   return Py_BuildValue("s", "");
	}else if (frmt.idx <= INT_64.idx){
	   return Py_BuildValue("l", long(0));
	}else if (frmt.idx <= UINT_64.idx){
	   return Py_BuildValue("k", unsigned(long(0)));
	}else if (frmt.idx  == FLOAT_32.idx){
	   return Py_BuildValue("f", float(0.0));
	}else if (frmt.idx  == FLOAT_64.idx){
	   return Py_BuildValue("d", double(0.0));
	}else{		
		Py_INCREF(Py_None);
      return Py_None;
	}
		
}



Format HeaderUtil::decode_format_code(unsigned char code){
	if (code <= 0x7F){
        return POS_FIXINT;
    }else if (code <= 0x8F){
        return  FIXMAP;
    }else if (code <= 0x9F){
        return  FIXARRAY;
    }else if (code <= 0xBF){
        return FIXSTR;
    }else if (code >= 0xE0){
        return NEG_FIXINT;
    }else{
        switch(code){
            case 0xC0:
                return NIL;
            case 0xC1:
                return NEVER_USED;
            case 0xC2:
                return FALSE_FORMAT;
            case 0xC3:
                return TRUE_FORMAT;

            case 0xC4:
                return BIN_8;
            case 0xC5:
                return BIN_16;
            case 0xC6:
                return BIN_32;

            case 0xC7:
                return EXT_8;
            case 0xC8:
                return EXT_16;
            case 0xC9:
                return EXT_32;

            case 0xCA:
                return FLOAT_32;
            case 0xCB:
                return FLOAT_64;

            case 0xCC:
                return UINT_8;
            case 0xCD:
                return UINT_16;
            case 0xCE:
                return UINT_32;
            case 0xCF:
                return UINT_64;

            case 0xD0:
                return INT_8;
            case 0xD1:
                return INT_16;
            case 0xD2:
                return INT_32;
            case 0xD3:
                return INT_64;

            case 0xD4:
                return FIXEXT_1;
            case 0xD5:
                return FIXEXT_2;
            case 0xD6:
                return FIXEXT_4;
            case 0xD7:
                return FIXEXT_8;
            case 0xD8:
                return FIXEXT_16;

            case 0xD9:
                return STR_8;
            case 0xDA:
                return STR_16;
            case 0xDB:
                return STR_32;

            case 0xDC:
                return ARRAY_16;
            case 0xDD:
                return ARRAY_32;

            case 0xDE:
                return MAP_16;
            case 0xDF:
                return MAP_32;
        }
    
    }
    return ERROR;
}




Template HeaderUtil::decode_template_idx(unsigned int idx){
	switch(idx){
         case 36:
             return TEMPLATE_POS_FIXINT;
         case 37:
             return TEMPLATE_NEG_FIXINT;

         case 21:
             return TEMPLATE_FIXMAP;
         case 20:
             return TEMPLATE_FIXARRAY;         
         case 7:
             return TEMPLATE_FIXSTR;

         case 34:
             return TEMPLATE_NIL;
         case 35:
             return TEMPLATE_NEVER_USED;

         case 32:
             return TEMPLATE_FALSE;
         case 33:
             return TEMPLATE_TRUE;

         case 1:
             return TEMPLATE_BIN_8;
         case 2:
             return TEMPLATE_BIN_16;
         case 3:
             return TEMPLATE_BIN_32;

         case 29:
             return TEMPLATE_EXT_8;
         case 30:
             return TEMPLATE_EXT_16;
         case 31:
             return TEMPLATE_EXT_32;

         case 16:
             return TEMPLATE_FLOAT_32;
         case 17:
             return TEMPLATE_FLOAT_64;

         case 12:
             return TEMPLATE_UINT_8;
         case 13:
             return TEMPLATE_UINT_16;
         case 14:
             return TEMPLATE_UINT_32;
         case 15:
             return TEMPLATE_UINT_64;

         case 8:
             return TEMPLATE_INT_8;
         case 9:
             return TEMPLATE_INT_16;
         case 10:
             return TEMPLATE_INT_32;
         case 11:
             return TEMPLATE_INT_64;

         case 24:
             return TEMPLATE_FIXEXT_1;
         case 25:
             return TEMPLATE_FIXEXT_2;
         case 26:
             return TEMPLATE_FIXEXT_4;
         case 27:
             return TEMPLATE_FIXEXT_8;
         case 28:
             return TEMPLATE_FIXEXT_16;

         case 4:
             return TEMPLATE_STR_8;
         case 5:
             return TEMPLATE_STR_16;
         case 6:
             return TEMPLATE_STR_32;

         case 18:
             return TEMPLATE_ARRAY_16;
         case 19:
             return TEMPLATE_ARRAY_32;

         case 22:
             return TEMPLATE_MAP_16;
         case 23:
             return TEMPLATE_MAP_32;
             
         case -2:
             return TEMPLATE_NONE;
      }
      return TEMPLATE_ERROR;
}
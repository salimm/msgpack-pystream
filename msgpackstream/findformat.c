#include <Python.h>
#include <stdio.h>
#include <string.h>


// inline  struct Format {int idx, unsigned char code, unsigned  char mask);

struct Format{
    int idx;
    unsigned char code;
    unsigned char mask;    
};

const struct Format POS_FIXINT = {36, 0x00 , 0x80};
const struct Format NEG_FIXINT = {37, 0xE0 , 0xE0};

const struct Format FIXMAP = {21, 0x80 , 0xF0};
const struct Format FIXARRAY = {20, 0x90 , 0xF0};
const struct Format FIXSTR = {7, 0xA0 , 0xE0};

const struct Format NIL = {34, 0xC0 , 0xFF};
const struct Format NEVER_USED = {35, 0xC1 , 0xFF};

const struct Format FALSE_FORMAT = {32, 0xC2 , 0xFF};
const struct Format TRUE_FORMAT = {33, 0xC3 , 0xFF};

const struct Format BIN_8 = {1, 0xC4 , 0xFF};
const struct Format BIN_16 = {2, 0xC5 , 0xFF};
const struct Format BIN_32 = {3, 0xC6 , 0xFF};

const struct Format EXT_8 = {29, 0xC7 , 0xFF};
const struct Format EXT_16 = {30, 0xC8 , 0xFF};
const struct Format EXT_32 = {31, 0xC9 , 0xFF};


const struct Format FLOAT_32 = {16, 0xCA , 0xFF};
const struct Format FLOAT_64 = {17, 0xCB , 0xFF};

const struct Format UINT_8 = {12, 0xCC , 0xFF};
const struct Format UINT_16 = {13, 0xCD , 0xFF};
const struct Format UINT_32 = {14, 0xCE , 0xFF};
const struct Format UINT_64 = {15, 0xCF , 0xFF};

const struct Format INT_8 = {8, 0xD0 , 0xFF};
const struct Format INT_16 = {9, 0xD1 , 0xFF};
const struct Format INT_32 = {10, 0xD2 , 0xFF};
const struct Format INT_64 = {11, 0xD3 , 0xFF};

const struct Format FIXEXT_1 = {24, 0xD4 , 0xFF};
const struct Format FIXEXT_2 = {25, 0xD5 , 0xFF};
const struct Format FIXEXT_4 = {26, 0xD6 , 0xFF};
const struct Format FIXEXT_8 = {27, 0xD7 , 0xFF};
const struct Format FIXEXT_16 = {28, 0xD8 , 0xFF};

const struct Format STR_8 = {4, 0xD9 , 0xFF};
const struct Format STR_16 = {5, 0xDA , 0xFF};
const struct Format STR_32 = {6, 0xDB , 0xFF};

const struct Format ARRAY_16 = {18, 0xDC , 0xFF};
const struct Format ARRAY_32 = {19, 0xDD , 0xFF};

const struct Format MAP_16 = {22, 0xDE , 0xFF};
const struct Format MAP_32 = {23, 0xDF , 0xFF};

const struct Format ERROR = {-1, 0 , 0};




// inline  struct Format {int idx, unsigned char code, unsigned  char mask){
//     struct Format frmt;
//     frmt.idx = idx; 
//     frmt.code = code;
//     frmt.mask = mask;
//     return frmt;
// }


const struct Format find_format_inner(unsigned char code){
    unsigned char firstbits = code & 0xF0;

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


const int find_format_code_inner(unsigned char code){
    unsigned char firstbits = code & 0xF0;
    
    if (firstbits < 0x80){
        return POS_FIXINT.code;
    }else if (code < 0xC0){        
        if (firstbits == 0xA0){
            return FIXSTR.code;
        }else if (firstbits == 0x90){
            return  FIXARRAY.code;
        }else if (firstbits == 0x80){        
            return  FIXMAP.code;
        }else{
            return -1;
        }
    }else{

            if (firstbits >= 0xE0){
                return NEG_FIXINT.code;
            }else{
                return code;
            }

    }
}

const int twos_comp(int val, int bits){
    if ((val & (1<<(bits-1))) !=0){
        return val - (1<<bits);
    }
    return val;
}

const PyObject * get_value(unsigned char byte, unsigned char code, unsigned char mask){
    if (code == NIL.code){
        Py_INCREF(Py_None);
        return Py_None;
    }else if(code == TRUE_FORMAT.code){
        return Py_BuildValue("O", Py_True);
    }else if(code == FALSE_FORMAT.code){
        return Py_BuildValue("O", Py_False);
    }else if(code == NEG_FIXINT.code){
        return Py_BuildValue("i", twos_comp(byte & ~mask,5));
    }else{
        return Py_BuildValue("i", byte & ~mask);
    }
}

static PyObject * find_format(PyObject *self, PyObject *args){
    const char *byte;
    const int *len;
    struct Format f  ;
    
    if (!PyArg_ParseTuple(args, "s#", &byte, &len))
        return NULL;
        
    
    f = find_format_inner(byte[0]);
    // if (code ==0){
    //     return NULL;
    // }
    return Py_BuildValue("{s:i,s:i,s:i}","code",f.code, "mask",f.mask, "idx", f.idx);

}

static PyObject * find_format_code(PyObject *self, PyObject *args){
    const char *byte;
    const int *len;
    struct Format f;
    
    
    if (!PyArg_ParseTuple(args, "s#", &byte, &len))
        return NULL;
    
    
        
    
    f  = find_format_inner(byte[0]);
    
    return Py_BuildValue("(i,i,i)",f.code, f.mask, f.idx);

}


static PyObject * parse_format_code(PyObject *self, PyObject *args){
    const char *byte;
    struct Format f;
    const int *len;
    const PyObject * val;
    
    if (!PyArg_ParseTuple(args, "s#", &byte, &len))
        return NULL;
    
    
    f = find_format_inner(byte[0]);
    
    val = get_value(byte[0], f.code, f.mask);
    return Py_BuildValue("(i,i,i,O)",f.code, f.mask, f.idx,val);
}





PyMODINIT_FUNC
initmsgpackfinder(void)
{
    static PyMethodDef FindMethods[] = {
        
        {"find_format",  find_format, METH_VARARGS,
            "find_format..."},
        {"find_format_code",  find_format_code, METH_VARARGS,
            "find_format_code..."},
        {"parse_format_code",  parse_format_code, METH_VARARGS,
            "parse_format_code..."},
        
        {NULL, NULL, 0, NULL}        /* Sentinel */
    };

    (void) Py_InitModule("msgpackfinder", FindMethods);
}


int
main(int argc, char *argv[])
{
    /* Pass argv[0] to the Python interpreter */
    Py_SetProgramName(argv[0]);

    /* Initialize the Python interpreter.  Required. */
    Py_Initialize();

    /* Add a static module */
    initmsgpackfinder();
    
}

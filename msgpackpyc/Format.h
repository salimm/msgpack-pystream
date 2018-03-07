#ifndef FORMAT_H
#define FORMAT_H

// struct used to contain information needed for a data segment format
struct Format{
    int idx;
    unsigned char code;
    unsigned char mask;
};

//--------------------------------------------------------
//------------------ List of Format type ---------------------
//--------------------------------------------------------


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
const struct Format NONE_FRMT = {-2, 0 , 0};


#endif



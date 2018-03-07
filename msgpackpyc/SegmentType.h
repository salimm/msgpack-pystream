
#ifndef SEGMENTTYPE_H
#define SEGMENTTYPE_H


// enum for segment type. Segment type contains information regarding on how the header should be used and what should be expected to be followed by
enum SegmentType{
    SEG_HEADER_VALUE_PAIR = 1,  // one header and multiple bytes for value
    SEG_HEADER_WITH_LENGTH_VALUE_PAIR = 2,  // one header, it also includes length of value paired with value which of variable length
    SEG_VARIABLE_LENGTH_VALUE = 3,  // 1 byte for header, multiple bytes for number of items, items
        
    SEG_SINGLE_BYTE = 4,  // head contain value
    
    
    SEG_EXT_FORMAT = 5,
    SEG_FIXED_EXT_FORMAT = 6,

    SEG_NONE_SEG = -1
};


#endif


#ifndef VALUETYPE_H
#define VALUETYPE_H


// type of value. It can be raw or nested. Nested includes arrays and maps
enum ValueType{
    VALUE_RAW = 1,
    VALUE_NESTED = 2,
    VALUE_NONE_VAL = 3
};


#endif

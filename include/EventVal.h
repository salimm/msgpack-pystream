
#ifndef EVANTVALTYPE_H
#define EVANTVALTYPE_H

enum EventValType{
    VAL_INT = 1,
    VAL_UINT = 2,

    VAL_FLOAT32 = 3,
    VAL_FLOAT64 = 4,

    VAL_STR = 5,        
    VAL_BIN = 6,
        
    VAL_NONE = 6,
    VAL_EXT = 7,
};


#endif



#ifndef EVANTVAL_H
#define EVANTVAL_H

struct EventVal{
    EventValType valtype;
    boost::variant<double, int, float, unsigned int, std::string> value;
};


#endif

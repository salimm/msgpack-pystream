#ifndef EVENTTYPE_H
#define EVENTTYPE_H


// event type for output
enum EventType{
    ET_VALUE = 1,  // value event
    ET_ARRAY_START = 2,  // event that indicates start of an array
    ET_ARRAY_END = 3,  // event that indicates end of an array
    ET_MAP_START = 4,  // event that indicates start of a map
    ET_MAP_END = 5,  // event that indicates end of a map
    ET_MAP_PROPERTY_NAME = 6,  // event that indicates property name
    ET_EXT = 7,  // event that indicates ext value

    ET_NONE_EVENT = -1
};


#endif
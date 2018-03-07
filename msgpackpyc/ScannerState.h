#ifndef SCANNERSTATE_H
#define SCANNERSTATE_H


// enum for scanner state
enum ScannerState{
    SC_IDLE = 1,  // parser just started or has processed all given data successfully (no buffer exists)
    SC_WAITING_FOR_HEADER = 2,  // expecting a header byte to be read next
    SC_WAITING_FOR_EXT_TYPE = 3,  // expecting an extension type segment
    SC_WAITING_FOR_LENGTH = 4,  // expecting length of the value to be read next
    SC_WAITING_FOR_VALUE = 5,  // expecting value to be read first
    SC_SEGMENT_ENDED = 6,  // segment finished parsing

    SC_NONE_SCSTATE = -1
};

#endif

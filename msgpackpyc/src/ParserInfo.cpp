#include "ParserInfo.h"

ParserInfo::ParserInfo(){
    std::string empty("");
    this->memory = empty;
    this->scstate = SC_IDLE;
    this->state = ParserState();
    this->waitingforprop = 0;
    this->parentismap = 0;    
    this->events = PyList_New(0);
}

ParserInfo::ParserInfo(const std::string &memory, enum ScannerState scstate, ParserState state, int waitingforprop, int parentismap){
    this->memory = memory;
    this->scstate = scstate;
    this->state = state;
    this->waitingforprop = waitingforprop;
    this->parentismap = parentismap;
    this->events = PyList_New(0);
    
}

ParserInfo::ParserInfo(const std::string &memory, enum ScannerState scstate, ParserState state,std::stack<ParserState> &stck , int waitingforprop, int parentismap){
    this->memory = memory;
    this->scstate = scstate;
    this->state = state;
    this->waitingforprop = waitingforprop;
    this->parentismap = parentismap;
    this->stck = stck;
    this->events = PyList_New(0);
}


ParserInfo::~ParserInfo(){
}
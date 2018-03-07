#include "ParserInfo.h"


ParserInfo::ParserInfo(){
    this->memory = "";
    this->scstate = SC_IDLE;
    ParserState state;
    this->state = state;
    this->waitingforprop = 0;
    this->parentismap = 0;
    // std::list<Event> events;
    // this->events = events;
}

ParserInfo::ParserInfo(const std::string &memory, enum ScannerState scstate, ParserState state, int waitingforprop, int parentismap){
    this->memory = memory;
    this->scstate = scstate;
    this->state = state;
    this->waitingforprop = waitingforprop;
    this->parentismap = parentismap;
    
}

ParserInfo::ParserInfo(const std::string &memory, enum ScannerState scstate, ParserState state,std::stack<ParserState> &stck , int waitingforprop, int parentismap){
    this->memory = memory;
    this->scstate = scstate;
    this->state = state;
    this->waitingforprop = waitingforprop;
    this->parentismap = parentismap;
    this->stck = stck;
}

ParserInfo::ParserInfo(const std::string &memory, enum ScannerState scstate, ParserState state, std::list<Event> &events , int waitingforprop, int parentismap){
    this->memory = memory;
    this->scstate = scstate;
    this->state = state;
    this->waitingforprop = waitingforprop;
    this->parentismap = parentismap;
    this->events = events;

}





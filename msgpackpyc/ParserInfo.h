#ifndef PARSERINFO_H
#define PARSERINFO_H

#include <algorithm>
#include <string>
#include <stack>
#include <list>
#include "Event.h"
#include "ParserState.h"
#include "ScannerState.h"

 


 // Circle class declaration
class ParserInfo {
private:   // Accessible by members of this class only
   
public:    // Accessible by ALL
	std::stack <ParserState> stck;
	std::string memory;
	enum ScannerState scstate;
	ParserState state;
	std::list<Event> events;
	int waitingforprop;
	int parentismap;


   // Constructor with default values
   ParserInfo(); 

   ParserInfo(const std::string &memory, enum ScannerState scstate, ParserState state, int waitingforprop, int parentismap); 

   ParserInfo(const std::string &memory, enum ScannerState scstate, ParserState state,std::stack<ParserState> &stck , int waitingforprop, int parentismap); 

   ParserInfo(const std::string &memory, enum ScannerState scstate, ParserState state,std::list<Event> &events , int waitingforprop, int parentismap); 
};




#endif
#ifndef PARSERSTATE_H
#define PARSERSTATE_H

#include "EventType.h"
#include "Format.h"
#include "Template.h"
 


 // Circle class declaration
class ParserState {
private:   // Accessible by members of this class only
   int length;
public:    // Accessible by ALL
   // Declare prototype of member functions   
   struct Format formattype;
   Template templatetype;   
   int remaining;
   int extcode;
   // Constructor with default values
   ParserState(); 

   ParserState(const struct Format &formattype, const struct Template &templatetype, int length, int extcode); 

   ParserState(const struct Format &formattype, const struct Template &templatetype, int length, int remaining, int extcode);

   int get_length();

   void set_length(int l);
};



#endif
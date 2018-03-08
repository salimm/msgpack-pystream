#ifndef EXTTYPE_H
#define EXTTYPE_H

#include "Format.h"
 


 // Circle class declaration
class ExtType {
private:   // Accessible by members of this class only
   
public:    // Accessible by ALL
   // stack
   struct Format formattype;
   int extcode;
  
   // Constructor with default values
   ExtType(); 

   ExtType(struct Format formattype, int extcode); 
};




#endif

#include "ExtType.h"
 


 
ExtType::ExtType(){
	this-> formattype = NONE_FRMT;
	this-> extcode = 0;
}

ExtType::ExtType(struct Format formattype, int extcode){
	this-> formattype = formattype;
	this-> extcode = extcode;
}

#ifndef HEADERUTIL_H
#define HEADERUTIL_H

#include <string>
#include <vector>
#include "Template.h"
#include "Format.h"
 


 // Circle class declaration
class HeaderUtil {
private:   // Accessible by members of this class only

	std::vector<Format> frmtlookup;
	std::vector<Template> templatelookup;
   std::vector<PyObject * (* )(unsigned char ,const struct Format &frmt)> fval_lookup;


   Format decode_format_code(unsigned char code);

   Template decode_template_idx(unsigned int idx);

   // creates lookup table  for format
   void create_format_lookup();

   // creates lookup table for template
   void create_template_lookup();


   // creates value function lookup list
   void create_fval_lookup();
   
public:    // Accessible by ALL
   // Declare prototype of member functions   
   HeaderUtil(); 

   // find the format for code
   Format& find_format(unsigned char code);

   // find the format for code
   Template& find_template(const struct Format &frmt);

   // find the format for code
   Template& find_template(unsigned char code);
   
	
	// extracts value from header byte 
	PyObject*  get_value(unsigned char byte, const struct Format &frmt);

   // extracts value from header byte 
   int  get_int_value(unsigned char byte, const struct Format &frmt);

	PyObject*  empty_value(const struct Format &frmt );


   
};


#endif

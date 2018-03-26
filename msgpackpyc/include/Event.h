#ifndef EVENT_H
#define EVENT_H

#include <string>
#include "EventType.h"
#include "Format.h"
#include "ExtType.h"
// #include "EventVal.h"
#include <Python.h>
 


 // Circle class declaration
class Event {
private:   // Accessible by members of this class only
   
public:    // Accessible by ALL
   // Declare prototype of member functions
   enum EventType eventtype;
   PyObject*  format;
   PyObject* value;
   // Constructor with default values
   Event(); 

   // Event(enum EventType eventtype, Format format, EventVal value); 
   Event(enum EventType eventtype, struct Format format, PyObject* value); 

   Event(enum EventType eventtype, struct Format format); 

   // Event(enum EventType eventtype, Format format, EventVal value); 
   Event(enum EventType eventtype,  ExtType exttype, PyObject* value); 

   Event(enum EventType eventtype,  ExtType exttype); 

   ~Event(); 

};


#endif
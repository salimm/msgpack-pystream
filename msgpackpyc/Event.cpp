#include "Event.h"

Event::Event(){
	this->eventtype = ET_VALUE;
 	this->format = POS_FIXINT;
 	Py_INCREF(Py_None);
 	PyObject* val =  Py_None;
 	this->value = val;
} 

Event::Event(enum EventType eventtype, boost::variant<Format, ExtType> format , PyObject* value){
 	this->eventtype = eventtype;
 	this->format = format;
 	this->value = value; 	
 }



Event::Event(enum EventType eventtype, boost::variant<Format, ExtType> format ){
 	this->eventtype = eventtype;
 	this->format = format;
 	PyObject* val =  Py_None;
 	this->value = val;
 }

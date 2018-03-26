#include "Event.h"
#include <iostream>

PyObject* convert(struct Format frmt){
	Py_INCREF(Py_None);
	return Py_BuildValue("(i,O)", frmt.code,Py_None);
}


PyObject* convert(ExtType exttype){
	return Py_BuildValue("(i,i)",exttype.formattype.code, exttype.extcode);
}

Event::Event(){
	this->eventtype = ET_VALUE;
 	this->format = convert(NONE_FRMT);
 	Py_INCREF(Py_None);
 	PyObject* val =  Py_None;
 	this->value = val;
} 

Event::Event(enum EventType eventtype, struct Format format , PyObject* value){
 	this->eventtype = eventtype;
 	this->format = convert(format);
 	this->value = value; 	
 }



Event::Event(enum EventType eventtype, struct Format format ){
 	this->eventtype = eventtype;
 	this->format = convert(format);
 	PyObject* val =  Py_None;
 	this->value = val;
 }

 Event::Event(enum EventType eventtype, ExtType exttype , PyObject* value){
 	this->eventtype = eventtype;
 	this->format = convert(exttype);
 	this->value = value; 	
 } 



Event::Event(enum EventType eventtype, ExtType exttype ){
 	this->eventtype = eventtype;
 	this->format = convert(exttype);
 	PyObject* val =  Py_None;
 	this->value = val;
 }



Event::~Event(){
	// Py_DECREF(this->value);
	// Py_DECREF(this->format);
	// std::cout << "working!!";
}
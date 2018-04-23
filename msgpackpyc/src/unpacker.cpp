#include <iostream>
#include <string>
#include <cstdlib>
#include <stdexcept>
#include "unpacker.h"

union FloatU{ 
	char b[4];
	float f;
};
union DoubleU{ 
	char b[8];
	double d;
};

unsigned int i =1;
bool little_endian_flag = (*((char*)&i));
/**
	handles reading header byte and determining next step and creating state
*/
void handle_read_header(ParserInfo &pinfo, HeaderUtil &hutil, const char header, PyObject* EXT_TYPE, PyObject* EVENT_TYPE);
/**
	handles reading length of value to be read
*/
void handle_read_length(ParserInfo &pinfo, HeaderUtil &hutil, int start, int end, PyObject* EXT_TYPE, PyObject* EVENT_TYPE);
/**
	handles reading value based  length of available
*/
void handle_read_value(ParserInfo &pinfo, int start, int end,PyObject* deserializers, PyObject* EXT_TYPE, PyObject* EVENT_TYPE);
/**
	handle reading ext type value or calling appropriate deserializer
*/
void handle_read_ext_type(ParserInfo &pinfo, int start,PyObject* deserializers, PyObject* EXT_TYPE, PyObject* EVENT_TYPE);
/**
	handle segment end and stack
*/
void handle_end_segment(ParserInfo &pinfo, PyObject* EXT_TYPE, PyObject* EVENT_TYPE);
/**
	assigns the next scanner state based on nested parent
*/
ScannerState get_state_after_raw(ParserInfo& pinfo);
/**
	function to change event type to Map Property Name if nested in map
*/
EventType value_event_type (ParserInfo &pinfo, enum EventType eventtype);
/**
	parse values from byte stream
**/
unsigned int  parse_uint(std::string &txt, int start , int end, bool little_endian);
int  parse_int(std::string &txt, int start , int end, bool little_endian);
int  parse_byte(std::string &txt, int start , int end, bool little_endian);
unsigned long long  parse_ulong(std::string &txt, int start , int end, bool little_endian);
long long  parse_long(std::string &txt, int start , int end, bool little_endian);
/**
	cop string from byte stream
*/
std::string  parse_str(std::string &txt, int start , int end, bool little_endian);


/**
	This is used to parse value from the given the segment
*/
PyObject* parse_value(ParserInfo &pinfo,Format ftype, int start, int end);

/**
	Process the input buffer. The buffer can contains all or a segment of the bytes from the complete message. 
    The function will buffer what will require extra bytes to be processed.
*/

void do_process_inner(std::string& buff, ParserInfo& context, PyObject* deserializers, PyObject* EXT_TYPE, PyObject* EVENT_TYPE);
// void do_process(std::string buff, ParserInfo& context, PyObject* deserializers);

/**
	create event function
*/
PyObject* create_event(enum EventType eventtype, struct Format format , PyObject* value, PyObject* EXT_TYPE, PyObject* EVENT_TYPE);
PyObject* create_event(enum EventType eventtype, struct Format format, PyObject* EXT_TYPE , PyObject* EVENT_TYPE);
PyObject* create_event_ext(enum EventType eventtype, ExtType exttype, PyObject* value, PyObject* deserializers, PyObject* EXT_TYPE, PyObject* EVENT_TYPE);
PyObject* create_event_ext(enum EventType eventtype, ExtType exttype, PyObject* deserializers, PyObject* EXT_TYPE, PyObject* EVENT_TYPE);
/**
	deserialize using custom deserializer
*/
PyObject* deserialize(PyObject* deserializers,PyObject* exttype ,int extcode, PyObject* buff, Py_ssize_t start, Py_ssize_t end );

void list_append(PyObject* list, PyObject* val);





void do_process(std::string& buff, ParserInfo& context, PyObject* deserializers){
	////std::cout << "====================== de process 1\n";
	
	PyObject *module = PyImport_ImportModule("msgpackstream.defs");
    if (!module)
      throw std::runtime_error("can't import ");
	////std::cout << "====================== de process 2\n";
  	PyObject* EXT_TYPE = PyObject_GetAttrString(module, "ExtType");
  	PyObject* EVENT_TYPE = PyObject_GetAttrString(module, "EventType");
	//std::cout << "====================== de process 3\n";
  	do_process_inner(buff, context, deserializers, EXT_TYPE, EVENT_TYPE);
	//std::cout << "====================== de process 4\n";
  	Py_DECREF(EXT_TYPE);
  	Py_DECREF(EVENT_TYPE);
  	Py_DECREF(module);
	//std::cout << "====================== de process 5\n";
}


void do_process_inner(std::string &buff, ParserInfo& context, PyObject* deserializers, PyObject* EXT_TYPE, PyObject* EVENT_TYPE){
	//std::cout << "-------------------------------1\n";
	Py_XDECREF(context.events);

	// creating the new state
	ParserInfo pinfo(context.memory + buff, context.scstate, context.state,context.stck, context.waitingforprop, context.parentismap);
	HeaderUtil hutil; 

	// index of the pointer on reading the input buff
	int idx = 0; 
	long int available = pinfo.memory.length();
	int advance = 1;
	//std::cout << "-------------------------------2\n";
	// process input while exists
	while (available >= advance){
		//std::cout << "-------------------------------3\n";
		// struct Format formattype;
		//expected start of a new segment
		if (pinfo.scstate <= SC_WAITING_FOR_HEADER){
			//std::cout << "-------------------------------4\n";
			advance = 1;	
			handle_read_header(pinfo, hutil, pinfo.memory[idx], EXT_TYPE, EVENT_TYPE);		

		// the scanner expects to read one or multiple bytes that contain an 
        // integer contain the length of the value to be expected
		}else if (pinfo.scstate == SC_WAITING_FOR_LENGTH){
			//std::cout << "-------------------------------5\n";
			advance = pinfo.state.get_length();
			// checking if enough bytes are available to read the bytes required to obtain length of value
			if (available < advance){
				////std::cout << "-------------------------------6\n";
				break;
			}
			////std::cout << "-------------------------------7\n";
			handle_read_length(pinfo, hutil, idx, idx + advance, EXT_TYPE, EVENT_TYPE);

		// if the scanner is expecting to parse one or multiple bytes as the value of the segment
		}else if (pinfo.scstate == SC_WAITING_FOR_VALUE){
			//std::cout << "-------------------------------8\n";
			advance = pinfo.state.get_length();
			// checking if enough bytes are available to read segment value
			if (available < advance){
				////std::cout << "-------------------------------8.1\n";
				break;
			}
			handle_read_value(pinfo, idx, idx + advance,deserializers, EXT_TYPE, EVENT_TYPE);
			////std::cout << "-------------------------------8.2\n";
		// if the scanner is expecting to parse an extension
		}else if (pinfo.scstate == SC_WAITING_FOR_EXT_TYPE){
			//std::cout << "-------------------------------9\n";
			advance= 1;
			handle_read_ext_type(pinfo, idx, deserializers, EXT_TYPE, EVENT_TYPE);
		}
		//std::cout << "-------------------------------10\n";
		// if a data segment is ended
		if (pinfo.scstate == SC_SEGMENT_ENDED){
			//std::cout << "-------------------------------11\n";
			handle_end_segment(pinfo, EXT_TYPE, EVENT_TYPE);
		}
		//proceed with scanning
		// advancing pointers and decreasing available bytes in memory
		idx += advance;
		available -= advance;
		advance = 1;
		//std::cout << "-------------------------------12\n";
	}
	// setting the return values
	// finished processing all since it needed extra info
	context.memory = pinfo.memory.substr(idx,pinfo.memory.length());
	context.scstate = pinfo.scstate;
	context.state = pinfo.state;
	context.waitingforprop = pinfo.waitingforprop;
	context.parentismap = pinfo.parentismap;
	context.events = pinfo.events;
	context.stck = pinfo.stck;
	//std::cout << "-------------------------------3\n";
}


void handle_read_header(ParserInfo &pinfo, HeaderUtil &hutil, const char header, PyObject* EXT_TYPE, PyObject* EVENT_TYPE){
	// parsing format from header byte
	struct Format frmt = hutil.find_format(header);	
	// getting template
	struct Template tmpl = hutil.find_template(frmt);
	//getting segment type
	SegmentType segtype = tmpl.segmenttype;

	// setting future 	steps based on header type and segment type
	if(segtype == SEG_SINGLE_BYTE){
		// get next header
		pinfo.scstate = get_state_after_raw(pinfo);
		// TODO not creating state here can increase performance
		pinfo.state = ParserState(frmt, tmpl, 0, 0);		
		// add event to events
		list_append(pinfo.events, create_event(value_event_type(pinfo, ET_VALUE),frmt, hutil.get_value(header,frmt),EXT_TYPE, EVENT_TYPE));
		// list_append(pinfo.events, create_event(value_event_type(pinfo, ET_VALUE),frmt, hutil.get_value(header,frmt),EXT_TYPE, EVENT_TYPE));
	}else if(segtype == SEG_HEADER_VALUE_PAIR){
		pinfo.scstate = SC_WAITING_FOR_VALUE;
        pinfo.state = ParserState(frmt, tmpl, tmpl.length * tmpl.multiplier,0);
	}else if(segtype == SEG_HEADER_WITH_LENGTH_VALUE_PAIR){
		// getting length
		int seglength = hutil.get_int_value(header, frmt) * tmpl.multiplier;
		// setting state
		pinfo.state = ParserState(frmt, tmpl, seglength, 0);

		if (tmpl.valuetype == VALUE_NESTED){
			list_append(pinfo.events, create_event(tmpl.startevent, frmt,EXT_TYPE, EVENT_TYPE));
			if(seglength==0){
				pinfo.scstate = SC_SEGMENT_ENDED;
			}else{				
				if (tmpl.multiplier == 2){
					pinfo.parentismap = 1;
					pinfo.waitingforprop = 1;
				}else{
					pinfo.parentismap = 0;
					pinfo.waitingforprop = 0;
				}
				pinfo.stck.push(pinfo.state);
				pinfo.scstate = SC_WAITING_FOR_HEADER;
			}

		}else{
			if(seglength == 0){
				list_append(pinfo.events, create_event(value_event_type(pinfo, ET_VALUE),frmt, hutil.empty_value(frmt),EXT_TYPE, EVENT_TYPE));
				pinfo.scstate = get_state_after_raw(pinfo);
			}else{
				pinfo.scstate = SC_WAITING_FOR_VALUE;
			}
		}
	}else if(segtype == SEG_VARIABLE_LENGTH_VALUE){
		pinfo.scstate = SC_WAITING_FOR_LENGTH;
        pinfo.state = ParserState(frmt, tmpl, tmpl.length ,0);
	}else if(segtype == SEG_EXT_FORMAT){
		pinfo.scstate = SC_WAITING_FOR_LENGTH;
        pinfo.state = ParserState(frmt, tmpl, tmpl.length ,0);		
	}else if(segtype == SEG_FIXED_EXT_FORMAT){
		pinfo.scstate = SC_WAITING_FOR_EXT_TYPE;
        pinfo.state = ParserState(frmt, tmpl, tmpl.length ,0);		
	}else{
		throw std::runtime_error("Invalid segment type!!");
	}


}


void handle_read_length(ParserInfo &pinfo, HeaderUtil &hutil, int start, int end, PyObject* EXT_TYPE, PyObject* EVENT_TYPE){
	//set length of state
	int seglength = parse_uint(pinfo.memory, start, end,little_endian_flag) * pinfo.state.templatetype.multiplier;
	pinfo.state.set_length(seglength);
	if (pinfo.state.templatetype.valuetype == VALUE_NESTED){
		// add start nested event
		list_append(pinfo.events, create_event(pinfo.state.templatetype.startevent,pinfo.state.formattype,EXT_TYPE, EVENT_TYPE));
		// check seglentgh
		if (seglength == 0){
			pinfo.scstate = SC_SEGMENT_ENDED;
		}else{
			// check multiplier to see if is nested
			if (pinfo.state.templatetype.multiplier == 2){
				pinfo.parentismap = 1;
				pinfo.waitingforprop = 1;
			}else{
				pinfo.parentismap = 0;
				pinfo.waitingforprop = 0;
			}
			pinfo.stck.push(pinfo.state);
			pinfo.scstate = SC_WAITING_FOR_HEADER;
		}

	}else{
		if (pinfo.state.templatetype.segmenttype == SEG_EXT_FORMAT){
			pinfo.scstate = SC_WAITING_FOR_EXT_TYPE;
		}else{
			pinfo.scstate = SC_WAITING_FOR_VALUE;
			if (pinfo.state.get_length() ==0){ // TODO I think for not nested but with length like string but I'm not sure if it actually happens
				list_append(pinfo.events, create_event(value_event_type(pinfo, ET_VALUE),pinfo.state.formattype, hutil.empty_value(pinfo.state.formattype),EXT_TYPE, EVENT_TYPE));
				pinfo.scstate = get_state_after_raw(pinfo);// TODO check this                
                //TODO it was always setting it to segment end. Maybe it makes sense but double check
			}
		}
	}
}


void handle_read_value(ParserInfo &pinfo, int start, int end, PyObject* deserializers, PyObject* EXT_TYPE, PyObject* EVENT_TYPE){
	// extract current segment type
	Format ftype = pinfo.state.formattype;
	SegmentType segmenttype = pinfo.state.templatetype.segmenttype;

	// if segment is variable length type
	if (segmenttype <= SEG_VARIABLE_LENGTH_VALUE){		
        PyObject* value = parse_value(pinfo, ftype, start, end);
        list_append(pinfo.events, create_event(value_event_type(pinfo, ET_VALUE),ftype, value ,EXT_TYPE, EVENT_TYPE));
        pinfo.scstate = get_state_after_raw(pinfo);
    // if extension type
	}else if (segmenttype >= SEG_EXT_FORMAT){
		PyObject *value = parse_value(pinfo, ftype, start, end); 
		ExtType etype = ExtType(ftype, pinfo.state.extcode);       
        list_append(pinfo.events, create_event_ext(value_event_type(pinfo, ET_EXT), etype, value, deserializers ,EXT_TYPE, EVENT_TYPE));
        pinfo.scstate = get_state_after_raw(pinfo);
	}else{
		throw std::runtime_error("Handle Read Value!!");
	}

}


void handle_read_ext_type(ParserInfo &pinfo, int start,PyObject* deserializers, PyObject* EXT_TYPE, PyObject* EVENT_TYPE){
	int extcode = parse_byte(pinfo.memory, start, start +1,little_endian_flag);
	pinfo.state.extcode = extcode;
	pinfo.scstate = SC_WAITING_FOR_VALUE;

	if (pinfo.state.get_length() ==0){
		ExtType etype = ExtType(pinfo.state.formattype, pinfo.state.extcode);
        list_append(pinfo.events, create_event_ext(value_event_type(pinfo, ET_EXT), etype, Py_BuildValue("s", ""),deserializers, EXT_TYPE, EVENT_TYPE ));
        pinfo.scstate = get_state_after_raw(pinfo);
	}
}


void handle_end_segment(ParserInfo &pinfo, PyObject* EXT_TYPE, PyObject* EVENT_TYPE){

    if (pinfo.state.templatetype.endevent != ET_NONE_EVENT){
    	list_append(pinfo.events, create_event(pinfo.state.templatetype.endevent, pinfo.state.formattype ,EXT_TYPE, EVENT_TYPE));
    }

    // multiplier
    if (pinfo.state.templatetype.multiplier == 2){
    	pinfo.parentismap = 0;
		pinfo.waitingforprop = 0;
    }

    if (pinfo.stck.size() == 0){
    	pinfo.scstate = SC_IDLE;
    	return;
    }


    if (pinfo.state.templatetype.valuetype != VALUE_RAW){    	
    	pinfo.stck.top().remaining -= 1;
    }


    if (pinfo.stck.top().remaining == 0){
    	pinfo.scstate = SC_SEGMENT_ENDED;
    	pinfo.state = pinfo.stck.top();
    	pinfo.stck.pop();

    	if (pinfo.state.templatetype.multiplier == 2){
			pinfo.parentismap = 1;
			pinfo.waitingforprop = 1;
    	}

    	handle_end_segment(pinfo, EXT_TYPE,EVENT_TYPE);
    }else{
    	if(pinfo.stck.top().templatetype.multiplier == 2){
    		pinfo.parentismap = 1;
			pinfo.waitingforprop = 1;
    	}
    	pinfo.scstate = SC_WAITING_FOR_HEADER;
    }

}


ScannerState get_state_after_raw(ParserInfo& pinfo){
	// checking if there is nested segment as parent in stack
	if (pinfo.stck.size() >0){
		// getting the parent
		// decreasing the number of values needed to be read before fulfilling the parent
		pinfo.stck.top().remaining = pinfo.stck.top().remaining-1;
		// if all required values for nested parent is read return end of segment
		if (pinfo.stck.top().remaining == 0){
			return SC_SEGMENT_ENDED;
		}
	}
	// if there is no parent or parent's number of values is not yet fulfilled 
	//then continue reading values by setting scanner state to seek for header
	return 	SC_WAITING_FOR_HEADER;
}


EventType value_event_type (ParserInfo &pinfo, enum EventType eventtype){	
	if (pinfo.waitingforprop == 1){
		eventtype = ET_MAP_PROPERTY_NAME;
	}
	if (pinfo.parentismap == 1){
            pinfo.waitingforprop = 1 - pinfo.waitingforprop;
    }
	return eventtype;
}


unsigned int  parse_uint(std::string &txt, int start , int end, bool little_endian){
	unsigned int out = 0;
	if (!little_endian){
		for (int i = end-1; i >=0 ; i--)	
			out = (out << 8) | txt[i];
	}else{
		for (int i = start; i < end; i++){
			out = (out << 8) | ((unsigned char) txt[i]);
		}
	}
	return out;
}


unsigned long long parse_ulong(std::string &txt, int start , int end, bool little_endian){
	////std::cout << "++++++++++++++++++++++1\n";
	unsigned long long out = 0;
	if (!little_endian){
		for (int i = end-1; i >=0 ; i--)	{
			out = (out << 8) | ((unsigned char) txt[i]);
			////std::cout << "\n";
			////std::cout << (int)out;					
			////std::cout << "-";
			////std::cout << (int)((unsigned char) txt[i]);				
		}
	}else{
		for (int i = start; i < end; i++){
			out = (out << 8) | ((unsigned char) txt[i]);
			////std::cout << "\n";
			////std::cout << (int)out;					
			////std::cout << "-";
			////std::cout << (int)((unsigned char) txt[i]);					
		}
	}	
	////std::cout << "\n";
	////std::cout << out;
	return out;
}


long long parse_long(std::string &txt, int start , int end, bool little_endian){
	long long   out = 0;
	if (!little_endian){
		for (int i = end-1; i >=0 ; i--){	
			out = (out << 8) | ((unsigned char) txt[i]);
			////std::cout << (int)((unsigned char) txt[i]);
			////std::cout << "\n";
			////std::cout << out;
			////std::cout << "\n";
		}
	}else{
		////std::cout << "===3\n";
		for (int i = start; i < end; i++){
			out = (out << 8) | ((unsigned char) txt[i]);
			////std::cout << (int)((unsigned char) txt[i]);
			////std::cout << "\n";
			////std::cout << out;
			////std::cout << "\n";
		}
	}
	return out;
}


float  parse_float(std::string &txt, int start , int end, bool little_endian){
	FloatU o ;
	if (little_endian){		
		
		for (int i = start; i < end; i++){
			o.b[end-(i-start)-start-1] = ( txt[i]);
		}
	}else{		
		for (int i = start; i < end; i++){
			o.b[i-start] = ( txt[i]);
		}
	}
	return o.f;
}


double  parse_double(std::string &txt, int start , int end, bool little_endian){	
	DoubleU o ;
	if (little_endian){				
		for (int i = start; i < end; i++){
			o.b[end-(i-start)-start-1] = ( txt[i]);
		}
	}else{		
		for (int i = start; i < end; i++){			
			o.b[i-start] = ( txt[i]);
		}
	}
	return o.d;
}


int  parse_int(std::string &txt, int start , int end, bool little_endian){
	int out = 0;
	if (!little_endian){
		for (int i = end-1; i >=0 ; i--)	
			out = (out << 8) | ((unsigned char) txt[i]);
	}else{
		for (int i = start; i < end; i++)
			out = (out << 8) | ((unsigned char) txt[i]);
	}
	return out;
}


int  parse_short(std::string &txt, int start , int end, bool little_endian){
	short out = 0;
	if (!little_endian){
		for (int i = end-1; i >=0 ; i--)	
			out = (out << 8) | ((unsigned char) txt[i]);
	}else{
		for (int i = start; i < end; i++)
			out = (out << 8) | ((unsigned char) txt[i]);
	}
	return out;
}


int  parse_byte(std::string &txt, int start , int end, bool little_endian){
	char out = 0;
	if (little_endian){
		for (int i = start; i < end; i++)
			out = (out << 8) | (txt[i]);
	}else{		
		for (int i = end-1; i >=start ; i--)	
			out = (out << 8) | ( txt[i]);
	}	
	return out;
}


std::string  parse_str(std::string &txt, int start , int end){
	return  txt.substr(start, end);
}


PyObject* parse_value(ParserInfo &pinfo, Format ftype, int start, int end){
        
        if(ftype.code == FLOAT_32.code){
        	return Py_BuildValue("f", parse_float(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.code == FLOAT_64.code){ 
        	return Py_BuildValue("d", parse_double(pinfo.memory, start, end,little_endian_flag));
        }if (ftype.idx <= FIXSTR.idx){ 
        	return Py_BuildValue("s#",parse_str(pinfo.memory, start, end).c_str(), (end-start));
        }else if(ftype.idx == INT_8.idx){
        	return Py_BuildValue("i", parse_byte(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.idx == INT_16.idx){
        	return Py_BuildValue("i", parse_short(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.idx == INT_32.idx){
        	return Py_BuildValue("i", parse_int(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.idx <= INT_64.idx){
        	return Py_BuildValue("L", parse_long(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.idx <= UINT_32.idx){
        	return Py_BuildValue("I",parse_uint(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.idx <= UINT_64.idx){
        	return Py_BuildValue("L",parse_ulong(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.idx <= UINT_64.idx){
        	return Py_BuildValue("k",parse_uint(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.idx <= EXT_32.idx){
        	return Py_BuildValue("s#",parse_str(pinfo.memory, start, end).c_str(), (end-start));
        }else{
 			throw std::runtime_error("Type can't be parsed!!");       	
        }
}


PyObject* convert_type(struct Format frmt){
	return Py_BuildValue("i", frmt.code);
}


PyObject* convert_type(ExtType exttype, PyObject* EXT_TYPE){
	return  PyObject_CallFunctionObjArgs(EXT_TYPE, PyInt_FromLong(exttype.formattype.code),PyInt_FromLong(exttype.extcode), NULL);
}


PyObject* create_event(enum EventType eventtype, struct Format format , PyObject* value, PyObject* EXT_TYPE, PyObject* EVENT_TYPE){
	PyObject* event = PyTuple_New(3);

	PyObject* eventype_py = PyInt_FromLong(eventtype);
	PyTuple_SET_ITEM(event,0,eventype_py);
	PyTuple_SET_ITEM(event,1,convert_type(format));
 	PyTuple_SET_ITEM(event,2,value);
 	
 	return event;
 }


PyObject* create_event(enum EventType eventtype, struct Format format, PyObject* EXT_TYPE , PyObject* EVENT_TYPE){
	PyObject* event = PyTuple_New(3);
 	
 	PyObject* eventype_py = PyInt_FromLong(eventtype);
 	PyTuple_SET_ITEM(event,0,eventype_py);
 	PyTuple_SET_ITEM(event,1,convert_type(format));
 	
 	Py_INCREF(Py_None);
 	PyTuple_SET_ITEM(event,2,Py_None);

 	return event;
 }


 PyObject* create_event_ext(enum EventType eventtype, ExtType exttype , PyObject* value, PyObject* deserializers, PyObject* EXT_TYPE, PyObject* EVENT_TYPE){
 	PyObject* event = PyTuple_New(3); 	
	PyObject* eventype_py = PyInt_FromLong(eventtype);
	PyTuple_SET_ITEM(event,0,eventype_py);
	PyObject* exttype_py = convert_type(exttype, EXT_TYPE);
 	PyTuple_SET_ITEM(event,1,exttype_py);
 	PyTuple_SET_ITEM(event,2,deserialize(deserializers, exttype_py, exttype.extcode, value, 0, PyString_Size(value)));

 	return event;
 } 


PyObject* create_event_ext(enum EventType eventtype, ExtType exttype, PyObject* deserializers, PyObject* EXT_TYPE, PyObject* EVENT_TYPE){
	PyObject* event = PyTuple_New(3);
 	PyObject* eventype_py = PyInt_FromLong(eventtype);
 	PyTuple_SET_ITEM(event,0,eventype_py);
	// PyTuple_SET_ITEM(event,0,PyObject_CallFunctionObjArgs(EVENT_TYPE,eventype_py, NULL));
 	PyTuple_SET_ITEM(event,1,convert_type(exttype, EXT_TYPE));
 	Py_INCREF(Py_None);
 	PyTuple_SET_ITEM(event,2,Py_None);

 	return event;
 
}


PyObject* deserialize(PyObject* deserializers,PyObject* exttype ,int extcode, PyObject* buff, Py_ssize_t start, Py_ssize_t end ){
	PyObject* deserializer = PyDict_GetItem(deserializers, PyInt_FromLong(extcode));
	if (deserializer == NULL){
		return buff;
	}
	PyObject* startidx= PyInt_FromLong(start);
	PyObject* endidx= PyInt_FromLong(end);
	PyObject* method = PyString_FromString("deserialize");
	PyObject* val = PyObject_CallMethodObjArgs(deserializer, method, exttype, buff,  startidx, endidx, NULL );
	Py_DECREF(startidx);
	Py_DECREF(endidx);
	Py_DECREF(method);

	return val;
}


void list_append(PyObject* events, PyObject* val){
	PyList_Append(events, val);
	Py_DECREF(val);
}
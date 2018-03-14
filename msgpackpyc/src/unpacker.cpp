#include <iostream>
#include <string>
#include <stdexcept>
#include <cstdlib>

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
void handle_read_header(ParserInfo &pinfo, HeaderUtil &hutil, const char header);

/**
	handles reading length of value to be read
*/
void handle_read_length(ParserInfo &pinfo, HeaderUtil &hutil, int start, int end);

/**
	handles reading value based  length of available
*/
void handle_read_value(ParserInfo &pinfo, int start, int end);

/**
	handle reading ext type value or calling appropriate deserializer
*/
void handle_read_ext_type(ParserInfo &pinfo, int start);


/**
	handle segment end and stack
*/
void handle_end_segment(ParserInfo &pinfo);

/**
	assigns the next scanner state based on nested parent
*/
ScannerState get_state_after_raw(ParserInfo& pinfo);

/**
	function to change event type to Map Property Name if nested in map
*/
EventType value_event_type (ParserInfo &pinfo, enum EventType eventtype);


unsigned int  parse_uint(std::string &txt, int start , int end, bool little_endian);

int  parse_int(std::string &txt, int start , int end, bool little_endian);

int  parse_byte(std::string &txt, int start , int end, bool little_endian);

unsigned long  parse_ulong(std::string &txt, int start , int end, bool little_endian);

long  parse_long(std::string &txt, int start , int end, bool little_endian);

std::string  parse_str(std::string &txt, int start , int end, bool little_endian);


/**
	This is used to parse value from the given the segment
*/
PyObject* parse_value(ParserInfo &pinfo,Format ftype, int start, int end);

/**
	Process the input buffer. The buffer can contains all or a segment of the bytes from the complete message. 
    The function will buffer what will require extra bytes to be processed.
*/
void do_process(std::string buff, ParserInfo& context){
	// creating the new state
	ParserInfo pinfo(context.memory + buff, context.scstate, context.state,context.stck, context.waitingforprop, context.parentismap);
	HeaderUtil hutil; 



	//std::cout <<"----1 "+std::to_string(context.memory.length())+"  -  "+std::to_string(buff.length())+"\n";

	// index of the pointer on reading the input buff
	int idx = 0; 
	int available = pinfo.memory.length();
	int advance = 1;

	//std::cout << "available:  "+std::to_string(available)+"  \n";
	// //std::cout<< pinfo.
	// process input while exists
	while (available >= advance){
		////std::cout <<"----dop---1\n";

		////std::cout <<"----state--- "+std::to_string(pinfo.state.formattype.idx)+"  "+std::to_string(pinfo.state.templatetype.segmenttype)+"  "+std::to_string(pinfo.state.remaining)+"\n";
		// struct Format formattype;
   // Template templatetype;   
   // int remaining;
   // int extcode;
		//expected start of a new segment
		if (pinfo.scstate <= SC_WAITING_FOR_HEADER){
			////std::cout <<"----dop---2\n";
			advance = 1;	
			handle_read_header(pinfo, hutil, pinfo.memory[idx]);		

		// the scanner expects to read one or multiple bytes that contain an 
        // integer contain the length of the value to be expected
		}else if (pinfo.scstate == SC_WAITING_FOR_LENGTH){
			////std::cout <<"----dop---3\n";
			advance = pinfo.state.get_length();
			// checking if enough bytes are available to read the bytes required to obtain length of value
			if (available < advance){
				break;
			}
			////std::cout <<"----dop---4\n";
			handle_read_length(pinfo, hutil, idx, idx + advance);

		// if the scanner is expecting to parse one or multiple bytes as the value of the segment
		}else if (pinfo.scstate == SC_WAITING_FOR_VALUE){
			////std::cout <<"----dop---5\n";
			advance = pinfo.state.get_length();
			// checking if enough bytes are available to read segment value
			if (available < advance){
				break;
			}
			////std::cout <<"----dop---6\n";
			handle_read_value(pinfo, idx, idx + advance);

		// if the scanner is expecting to parse an extension
		}else if (pinfo.scstate == SC_WAITING_FOR_EXT_TYPE){
			////std::cout <<"----dop---7\n";
			advance= 1;
			handle_read_ext_type(pinfo, idx);
		}
		// if a data segment is ended
		if (pinfo.scstate == SC_SEGMENT_ENDED){
			////std::cout <<"----dop---8\n";
			handle_end_segment(pinfo);
		}

		//proceed with scanning

		////std::cout <<"----dop---9\n";

		// advancing pointers and decreasing available bytes in memory
		idx += advance;
		available -= advance;
		advance = 1;
	}




	////std::cout <<"----dop---10\n";


	// setting the return values

	// finished processing all since it needed extra info
	context.memory = pinfo.memory.substr(idx,pinfo.memory.length());
	context.scstate = pinfo.scstate;
	context.state = pinfo.state;
	context.waitingforprop = pinfo.waitingforprop;
	context.parentismap = pinfo.parentismap;
	context.events = pinfo.events;
	context.stck = pinfo.stck;

	// return context;
}







void handle_read_header(ParserInfo &pinfo, HeaderUtil &hutil, const char header){
	////std::cout <<"top header ---xxx \n";
	// parsing format from header byte
	struct Format frmt = hutil.find_format(header);	
	////std::cout <<"top header ---xxx "+std::to_string(frmt.idx)+"\n";
	// getting template
	struct Template tmpl = hutil.find_template(frmt);
	//getting segment type
	SegmentType segtype = tmpl.segmenttype;
	////std::cout <<"top header --- "+ std::to_string(frmt.idx) +"\n";

	// setting future 	steps based on header type and segment type
	if(segtype == SEG_SINGLE_BYTE){
		////std::cout <<"----header---1\n";
		// get next header
		pinfo.scstate = get_state_after_raw(pinfo);
		////std::cout <<"----header---2\n";
		// TODO not creating state here can increase performance
		pinfo.state = ParserState(frmt, tmpl, 0, 0);		
		////std::cout <<"----header---3\n";
		// add event to events
		////std::cout << std::	to_string(frmt.idx);
		pinfo.events.push_back(Event(value_event_type(pinfo, ET_VALUE),frmt, hutil.get_value(header,frmt)));
		////std::cout <<"----header---4\n";

	}else if(segtype == SEG_HEADER_VALUE_PAIR){
		////std::cout <<"----header---5\n";
		pinfo.scstate = SC_WAITING_FOR_VALUE;
        pinfo.state = ParserState(frmt, tmpl, tmpl.length * tmpl.multiplier,0);
	}else if(segtype == SEG_HEADER_WITH_LENGTH_VALUE_PAIR){
		//std::cout <<"----header---6\n";
		// getting length
		int seglength = hutil.get_int_value(header, frmt) * tmpl.multiplier;
		////std::cout <<"----header---7  length:"+std::to_string(seglength)+"\n";
		// setting state
		pinfo.state = ParserState(frmt, tmpl, seglength, 0);
		//std::cout << "{state remaining: "+std::to_string(pinfo.state.remaining) +" length:"+std::to_string(pinfo.state.get_length())+"\n";

		////std::cout <<"----header---8\n";
		if (tmpl.valuetype == VALUE_NESTED){
			////std::cout <<"----header---9\n";
			pinfo.events.push_back(Event(tmpl.startevent, frmt));
			if(seglength==0){
				////std::cout <<"----header---10\n";
				pinfo.scstate = SC_SEGMENT_ENDED;
			}else{				
				if (tmpl.multiplier == 2){
					////std::cout <<"----header---11\n";
					pinfo.parentismap = 1;
					pinfo.waitingforprop = 1;
				}else{
					////std::cout <<"----header---12\n";
					pinfo.parentismap = 0;
					pinfo.waitingforprop = 0;
				}
				pinfo.stck.push(pinfo.state);
				pinfo.scstate = SC_WAITING_FOR_HEADER;
			}

		}else{
			////std::cout <<"----header---13\n";
			if(seglength == 0){
				////std::cout <<"----header---14\n";
				pinfo.events.push_back(Event(value_event_type(pinfo, ET_VALUE),frmt, hutil.empty_value(frmt)));
				pinfo.scstate = get_state_after_raw(pinfo);
			}else{
				////std::cout <<"----header---15\n";
				pinfo.scstate = SC_WAITING_FOR_VALUE;
			}

		}
		////std::cout <<"----header---16\n";
	}else if(segtype == SEG_VARIABLE_LENGTH_VALUE){
		//std::cout <<"----header---17\n";		
		pinfo.scstate = SC_WAITING_FOR_LENGTH;
        pinfo.state = ParserState(frmt, tmpl, tmpl.length ,0);
        //std::cout << "{state remaining: "+std::to_string(pinfo.state.remaining) +" length:"+std::to_string(pinfo.state.get_length())+"\n";
	}else if(segtype == SEG_EXT_FORMAT){
		////std::cout <<"----header---18\n";
		pinfo.scstate = SC_WAITING_FOR_LENGTH;
        pinfo.state = ParserState(frmt, tmpl, tmpl.length ,0);		
	}else if(segtype == SEG_FIXED_EXT_FORMAT){
		////std::cout <<"----header---19\n";
		pinfo.scstate = SC_WAITING_FOR_EXT_TYPE;
        pinfo.state = ParserState(frmt, tmpl, tmpl.length ,0);		
	}else{
		////std::cout <<"----header---20\n";
		throw std::runtime_error("Invalid segment type!!");
	}


}


void handle_read_length(ParserInfo &pinfo, HeaderUtil &hutil, int start, int end){
	//set length of state
	int seglength = parse_uint(pinfo.memory, start, end,little_endian_flag) * pinfo.state.templatetype.multiplier;
	pinfo.state.set_length(seglength);
	// //std::cout << "****** lenght ** 1 "+ std::to_string(start)+" "+std::to_string(end);
	if (pinfo.state.templatetype.valuetype == VALUE_NESTED){
		// //std::cout << "****** lenght ** 2 ";
		// add start nested event
		pinfo.events.push_back(Event(pinfo.state.templatetype.startevent,pinfo.state.formattype));
		// check seglentgh
		if (seglength == 0){
			////std::cout << "****** lenght ** 3 ";
			pinfo.scstate = SC_SEGMENT_ENDED;
		}else{
			////std::cout << "****** lenght ** 4";
			// check multiplier to see if is nested
			if (pinfo.state.templatetype.multiplier == 2){
				////std::cout << "****** lenght ** 5 ";
				pinfo.parentismap = 1;
				pinfo.waitingforprop = 1;
			}else{
				////std::cout << "****** lenght ** 6 ";
				pinfo.parentismap = 0;
				pinfo.waitingforprop = 0;
			}
			////std::cout << "****** lenght ** 9 ";
			pinfo.stck.push(pinfo.state);
			pinfo.scstate = SC_WAITING_FOR_HEADER;
		}

	}else{
		////std::cout << "****** lenght ** 10 ";
		if (pinfo.state.templatetype.segmenttype == SEG_EXT_FORMAT){
			////std::cout << "****** lenght ** 11 ";
			pinfo.scstate = SC_WAITING_FOR_EXT_TYPE;
		}else{
			////std::cout << "****** lenght ** 12 ";
			pinfo.scstate = SC_WAITING_FOR_VALUE;
			if (pinfo.state.get_length() ==0){ // TODO I think for not nested but with length like string but I'm not sure if it actually happens
				////std::cout << "****** lenght ** 13 ";
				pinfo.events.push_back(Event(value_event_type(pinfo, ET_VALUE),pinfo.state.formattype, hutil.empty_value(pinfo.state.formattype)));
				pinfo.scstate = get_state_after_raw(pinfo);// TODO check this                
                //TODO it was always setting it to segment end. Maybe it makes sense but double check
			}
		}
	}
	
}


void handle_read_value(ParserInfo &pinfo, int start, int end){
	////std::cout << "****** value ** 1 "+ std::to_string(start)+" "+std::to_string(end);
	// extract current segment type
	Format ftype = pinfo.state.formattype;
	SegmentType segmenttype = pinfo.state.templatetype.segmenttype;

	// if segment is variable length type
	if (segmenttype <= SEG_VARIABLE_LENGTH_VALUE){		
        PyObject* value = parse_value(pinfo, ftype, start, end);
        pinfo.events.push_back(Event(value_event_type(pinfo, ET_VALUE),ftype, value ));
        pinfo.scstate = get_state_after_raw(pinfo);

    // if extension type
	}else if (segmenttype >= SEG_EXT_FORMAT){
		PyObject *value = parse_value(pinfo, ftype, start, end); 
		ExtType etype = ExtType(ftype, pinfo.state.extcode);       
        pinfo.events.push_back(Event(value_event_type(pinfo, ET_EXT), etype, value ));
        pinfo.scstate = get_state_after_raw(pinfo);
	}else{
		throw std::runtime_error("Handle Read Value!!");
	}

}

void handle_read_ext_type(ParserInfo &pinfo, int start){
	int extcode = parse_byte(pinfo.memory, start, start +1,little_endian_flag);
	pinfo.state.extcode = extcode;
	pinfo.scstate = SC_WAITING_FOR_VALUE;

	if (pinfo.state.get_length() ==0){
		ExtType etype = ExtType(pinfo.state.formattype, pinfo.state.extcode);
        pinfo.events.push_back(Event(value_event_type(pinfo, ET_EXT), etype, Py_BuildValue("s", "") ));
        pinfo.scstate = get_state_after_raw(pinfo);
	}
}


void handle_end_segment(ParserInfo &pinfo){

	////std::cout << "****** end ** 1 ";
	// 
    if (pinfo.state.templatetype.endevent != ET_NONE_EVENT){
    	////std::cout << "****** end ** 2 ";
    	pinfo.events.push_back(Event(pinfo.state.templatetype.endevent, pinfo.state.formattype ));
    }

    // multiplier
    if (pinfo.state.templatetype.multiplier == 2){
    	////std::cout << "****** end ** 3 ";
    	pinfo.parentismap = 0;
		pinfo.waitingforprop = 0;
    }

    if (pinfo.stck.size() == 0){
    	////std::cout << "****** end ** 4 ";
    	pinfo.scstate = SC_IDLE;
    	return;
    }


    if (pinfo.state.templatetype.valuetype != VALUE_RAW){    	
    	////std::cout << "****** end ** 5.1 "+std::to_string(pinfo.stck.top().remaining)+" "+std::to_string(pinfo.stck.top().formattype.idx);

    	pinfo.stck.top().remaining -= 1;
    	////std::cout << "****** end ** 5.2 "+std::to_string(pinfo.stck.top().remaining);

    }


    if (pinfo.stck.top().remaining == 0){
    	////std::cout << "****** end ** 6 ";
    	pinfo.scstate = SC_SEGMENT_ENDED;
    	pinfo.state = pinfo.stck.top();
    	pinfo.stck.pop();

    	if (pinfo.state.templatetype.multiplier == 2){
    		////std::cout << "****** end ** 7 ";
			pinfo.parentismap = 1;
			pinfo.waitingforprop = 1;
    	}

    	handle_end_segment(pinfo);
    }else{
    	////std::cout << "****** end ** 7 ";
    	if(pinfo.stck.top().templatetype.multiplier == 2){
    		////std::cout << "****** end ** 8 ";
    		pinfo.parentismap = 1;
			pinfo.waitingforprop = 1;
    	}
    	pinfo.scstate = SC_WAITING_FOR_HEADER;
    }
    ////std::cout << "****** end ** 9 ";

}



ScannerState get_state_after_raw(ParserInfo& pinfo){

	// checking if there is nested segment as parent in stack
	if (pinfo.stck.size() >0){
		////std::cout << "---- state before -- 0\n ";
		// getting the parent
		// decreasing the number of values needed to be read before fulfilling the parent
		////std::cout << "---- state before remaining:-- "+std::to_string(pinfo.stck.top().remaining)+"\n ";
		pinfo.stck.top().remaining = pinfo.stck.top().remaining-1;
		////std::cout << "---- state after remaining: -- "+std::to_string(pinfo.stck.top().remaining)+"\n ";
		// if all required values for nested parent is read return end of segment
		if (pinfo.stck.top().remaining == 0){
			////std::cout << "seg end is next\n";
			return SC_SEGMENT_ENDED;
		}
	}
	////std::cout << "read header is next\n";
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



unsigned long  parse_ulong(std::string &txt, int start , int end, bool little_endian){
	unsigned long out = 0;
	if (!little_endian){
		for (int i = end-1; i >=0 ; i--)	
			out = (out << 8) | ((unsigned char) txt[i]);
	}else{
		for (int i = start; i < end; i++)
			out = (out << 8) | ((unsigned char) txt[i]);
	}	
	return out;
}

long  parse_long(std::string &txt, int start , int end, bool little_endian){
	long out = 0;
	if (!little_endian){
		for (int i = end-1; i >=0 ; i--)	
			out = (out << 8) | ((unsigned char) txt[i]);
	}else{
		for (int i = start; i < end; i++)
			out = (out << 8) | ((unsigned char) txt[i]);
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

	// int out = 0;
	// if (little_endian){
	// 	for (int i = start; i < end; i++)
	// 		out = (out << 8) | (txt[i]);
	// }else{		
	// 	for (int i = end-1; i >=start ; i--)	
	// 		out = (out << 8) | ( txt[i]);
	// }	
	////std::cout << "********************* "+std::to_string(out)+"\n";
	// return out;
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
	// short out = 0;
	// if (little_endian){
	// 	for (int i = start; i < end; i++)
	// 		out = (out << 8) | (txt[i]);
	// }else{		
	// 	for (int i = end-1; i >=start ; i--)	
	// 		out = (out << 8) | ( txt[i]);
	// }	
	////std::cout << "********************* "+std::to_string(out)+"\n";
	// return out;
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
        	////std::cout << "vvvvvvvv 1\n";
        	return Py_BuildValue("f", parse_float(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.code == FLOAT_64.code){ 
        	////std::cout << "vvvvvvvv 2\n";
        	return Py_BuildValue("d", parse_double(pinfo.memory, start, end,little_endian_flag));
        }if (ftype.idx <= FIXSTR.idx){ 
        	////std::cout << "vvvvvvvv 3\n";
        	return Py_BuildValue("s#",parse_str(pinfo.memory, start, end).c_str(), (end-start));
        }else if(ftype.idx == INT_8.idx){
        	////std::cout << "vvvvvvvv 5\n";
        	return Py_BuildValue("i", parse_byte(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.idx == INT_16.idx){
        	////std::cout << "vvvvvvvv 6\n";
        	return Py_BuildValue("i", parse_short(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.idx == INT_32.idx){
        	////std::cout << "vvvvvvvv 7\n";
        	return Py_BuildValue("i", parse_int(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.idx <= INT_64.idx){
        	////std::cout << "vvvvvvvv 8\n";
        	return Py_BuildValue("l", parse_long(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.idx <= UINT_32.idx){
        	////std::cout << "vvvvvvvv 9\n";
        	return Py_BuildValue("I",parse_uint(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.idx <= UINT_64.idx){
        	////std::cout << "vvvvvvvv 10\n";
        	return Py_BuildValue("k",parse_ulong(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.idx <= UINT_64.idx){
        	////std::cout << "vvvvvvvv 11\n";
        	return Py_BuildValue("k",parse_uint(pinfo.memory, start, end,little_endian_flag));
        }else if(ftype.idx <= EXT_32.idx){
        	return Py_BuildValue("s#",parse_str(pinfo.memory, start, end).c_str(), (end-start));
        }else{
 			throw std::runtime_error("Type can't be parsed!!");       	
        }

}
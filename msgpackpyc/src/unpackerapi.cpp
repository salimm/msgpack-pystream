#include <iostream>
#include "unpacker.h"
#include "Event.h"
#include <Python.h>



ParserInfo convert_parser_info( PyObject *args);

PyObject* convert_pyobject(Event &event);


PyObject* convert_pyobject(ParserInfo &pinfo);

PyObject* convert_pyobject(ParserState &state);


Event& parse_event(PyObject* obj);

ParserState parse_state(PyObject* obj, HeaderUtil &hutil);


PyObject* process(PyObject *self, PyObject *args);





PyObject* process(PyObject *self, PyObject *args){

	
	PyObject* piobj;
	int memsize;
	const char* mem;

	if (!PyArg_ParseTuple(args, "s#O",  &mem, &memsize, &piobj))
        return NULL;
    // Py_INCREF(piobj);

	// HeaderUtil hutil;
   
    ParserInfo pinfo = convert_parser_info(piobj);
    // std::cout << "????????  1 "+std::to_string(pinfo.memory.size())+"\n";
    std::string memory(mem,memsize);
    // std::cout << "????????  2 "+memory+" |  "+std::to_string(memsize)+"\n";
	do_process(memory, pinfo);
	// std::cout << "???????	?  3\n";

	// return piobj;

	return convert_pyobject(pinfo);		
}

ParserInfo convert_parser_info( PyObject *piobj){
	Py_INCREF(piobj);

	std::list<Event> events;
	// PyObject* eventsobj = PyTuple_GetItem(piobj,4);
	// for (int i =0; i< PyList_Size(eventsobj);i++){
		// events.push_back(parse_event(PyList_GetItem(eventsobj, i)));
	// }
	// Py_DECREF(PyTuple_GetItem(piobj,4));

	HeaderUtil hutil;

	std::stack<ParserState> stck;
	PyObject* stackobj = PyTuple_GetItem(piobj,0);

	for (int i =PyList_Size(stackobj)-1; i>-1 ;i--){
		stck.push(parse_state(PyList_GetItem(stackobj, i), hutil));
	}
	// Py_DECREF(stackobj);
	int memlen   = int(PyInt_AsLong(PyTuple_GetItem(piobj,7)));
	std::string memory = std::string(PyString_AsString(PyTuple_GetItem(piobj,1)),memlen);
	// // Py_DECREF(PyTuple_GetItem(piobj,1));
	ScannerState scstate   = static_cast<ScannerState>(int(PyInt_AsLong(PyTuple_GetItem(piobj,2))));
	// // Py_DECREF(PyTuple_GetItem(piobj,2));

	ParserState state = parse_state(PyTuple_GetItem(piobj,3), hutil);
	// // Py_DECREF(PyTuple_GetItem(piobj,3));

	int waitingforprop   = int(PyInt_AsLong(PyTuple_GetItem(piobj,5)));
	// // Py_DECREF(PyTuple_GetItem(piobj,5));
	int parentismap   = int(PyInt_AsLong(PyTuple_GetItem(piobj,6)));
	// // Py_DECREF(PyTuple_GetItem(piobj,6));

	ParserInfo pinfo = ParserInfo(memory, scstate,state, stck , waitingforprop, parentismap );
	// pinfo.stck = stck;

	Py_DECREF(piobj);

	return pinfo;

	

}



// return Py_BuildValue("(i,i,i,i,i)",state.formattype.code, state.formattype.code, state.get_length(), state.remaining, state.extcode);

ParserState parse_state(PyObject* obj, HeaderUtil &hutil){
	Py_INCREF(obj);

	if(obj == Py_None){
		return ParserState();
	}
	int code = int(PyInt_AsLong(PyTuple_GetItem(obj,0)));
	int length = int(PyInt_AsLong(PyTuple_GetItem(obj,2)));
	int remaining = int(PyInt_AsLong(PyTuple_GetItem(obj,3)));
	int extcode = int(PyInt_AsLong(PyTuple_GetItem(obj,4)));
	struct Format frmt = hutil.find_format(code);
	struct Template tmpl = hutil.find_template(code);
	
	Py_DECREF(obj);

	return ParserState(frmt, tmpl, length, remaining, extcode);

	
}

PyObject* convert_pyobject(ParserInfo &pinfo){
	//std::cout << "xxxxxxxx  1\n";
	PyObject* events = PyList_New(pinfo.events.size());	
	int idx = 0;
	for (std::list<Event>::iterator it = pinfo.events.begin(); it != pinfo.events.end(); ++it){		
		PyList_SET_ITEM(events, idx, convert_pyobject(*it));
		idx++;
		// //std::cout << std::to_string(idx)+"\n";
	}
	// Py_INCREF(events);
	//std::cout << "xxxxxxxx  2\n";

	PyObject* stck = PyList_New(pinfo.stck.size());		
	idx = 0;
	while(pinfo.stck.size()!=0){
		//std::cout << "converting {state remaining: "+std::to_string(pinfo.stck.top().remaining) +" length:"+std::to_string(pinfo.stck.top().get_length())+"\n";
		PyList_SET_ITEM(stck, idx, convert_pyobject(pinfo.stck.top()));
		pinfo.stck.pop();
		idx++;
	}
	//std::cout << "xxxxxxxx  3\n";

	PyObject* state =  convert_pyobject(pinfo.state);

	//std::cout << "xxxxxxxx  4  "+std::to_string(pinfo.memory.size())+"\n";
	PyObject* out = Py_BuildValue("(O,s#,i,O,O,i,i)", stck, pinfo.memory.c_str(), pinfo.memory.size(), pinfo.scstate, state, events, pinfo.waitingforprop, pinfo.parentismap);
	Py_DECREF(stck);
	Py_DECREF(state);
	Py_DECREF(events);	

	return out;
	// return Py_BuildValue("(i,i)", 1,2);
	// return Py_BuildValue("i", 1);

}

PyObject* convert_pyobject(Event &event){
   // PyObject* tp ;
   // if( event.format.which() ==0){
   // 		Py_INCREF(Py_None);
   // 		tp = Py_BuildValue("(i,O)", boost::get<Format>(event.format).code,Py_None);
   // }else{
   // 		tp = Py_BuildValue("(i,i)",boost::get<ExtType>(event.format).formattype.code, boost::get<ExtType>(event.format).extcode);
   // }

   PyObject* res=Py_BuildValue("(i,O,O)", event.eventtype, event.format, event.value);	
   return res;

}

PyObject* convert_pyobject(ParserState &state){
	return Py_BuildValue("(i,i,i,i,i)",state.formattype.code, state.formattype.code, state.get_length(), state.remaining, state.extcode);
}


PyMODINIT_FUNC
initmpstream_cunpacker(void)
{
    static PyMethodDef FindMethods[] = {
        
        {"process",  process, METH_VARARGS,
            "processes a segment of instream..."},                
        {NULL, NULL, 0, NULL}        /* Sentinel */
    };

    (void) Py_InitModule("mpstream_cunpacker", FindMethods);
}


int
main(int argc, char *argv[])
{
    /* Pass argv[0] to the Python interpreter */
    Py_SetProgramName(argv[0]);

    /* Initialize the Python interpreter.  Required. */
    Py_Initialize();

    /* Add a static module */
    initmpstream_cunpacker();         
    
    // process(NULL, NULL);
}

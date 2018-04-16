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
	PyObject* deserializers;
	int memsize;
	const char* mem;

	if (!PyArg_ParseTuple(args, "s#OO",  &mem, &memsize, &piobj, &deserializers))
        return NULL;
    // Py_INCREF(piobj);

	// HeaderUtil hutil;
   
    ParserInfo pinfo = convert_parser_info(piobj);
    // std::cout << "????????  1 "+std::to_string(pinfo.memory.size())+"\n";
    std::string memory(mem,memsize);
    // std::cout << "????????  2 "+memory+" |  "+std::to_string(memsize)+"\n";
	do_process(memory, pinfo, deserializers);
	// std::cout << "???????	?  3\n";

	// return piobj;

	return convert_pyobject(pinfo);		
}

ParserInfo convert_parser_info( PyObject *piobj){
	Py_INCREF(piobj);

	// std::list<Event> events;
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
	// PyObject* events = PyList_New(pinfo.events.size());	
	// int idx = 0;
	// for (std::list<Event>::iterator it = pinfo.events.begin(); it != pinfo.events.end(); ++it){		
		// PyList_SET_ITEM(events, idx, convert_pyobject(*it));
		// idx++;
		// //std::cout << std::to_string(idx)+"\n";
	// }
	// Py_INCREF(events);
	//std::cout << "xxxxxxxx  2\n";

	PyObject* stck = PyList_New(pinfo.stck.size());		
	int idx = 0;
	while(pinfo.stck.size()!=0){
		//std::cout << "converting {state remaining: "+std::to_string(pinfo.stck.top().remaining) +" length:"+std::to_string(pinfo.stck.top().get_length())+"\n";
		PyList_SET_ITEM(stck, idx, convert_pyobject(pinfo.stck.top()));
		pinfo.stck.pop();
		idx++;
	}
	//std::cout << "xxxxxxxx  3\n";

	PyObject* state =  convert_pyobject(pinfo.state);

	//std::cout << "xxxxxxxx  4  "+std::to_string(pinfo.memory.size())+"\n";
	PyObject* out = Py_BuildValue("(O,s#,i,O,O,i,i)", stck, pinfo.memory.c_str(), pinfo.memory.size(), pinfo.scstate, state, pinfo.events, pinfo.waitingforprop, pinfo.parentismap);
	Py_DECREF(stck);
	Py_DECREF(state);
	// Py_DECREF(events);	

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





//####################################################################################
//####################################### iterator ###################################
//####################################################################################



typedef struct {
	PyObject_HEAD
	PyObject* instream;
	PyObject* parsers;
	int buffersize;
	long int idx;
	long int rem;
	ParserInfo* pinfo;
} cunpacker_EventStream;

// __iter__()  function
static PyObject* cunpacker_EventStream_iter(PyObject *self){
	
	// std::cout << "-------- init\n";
	Py_INCREF(self);	
	return self;
}


// next() implementation
static PyObject* cunpacker_EventStream_next(PyObject *self){
	// std::cout << "-------- next 1\n";
	cunpacker_EventStream *p = (cunpacker_EventStream *)self;
	// std::cout << "-------- next 2\n";
	if(p->idx >= p->rem){
		// std::cout << "-------- next 3\n";		
		Py_XDECREF(p->pinfo->events);
		// std::cout << "---"+std::to_string(p->pinfo->events->ob_refcnt)+"\n";
		// p->pinfo->events = PyList_New(0);
		p->rem = 0;
		p->idx = 0;
		// std::cout << "-------- next 4\n";

		PyObject* method =PyString_FromString((char*)"read");
		while(p->rem==0){
			// std::cout << "-------- next 5\n";
			
			PyObject* bfsize = PyInt_FromLong(p->buffersize);
			PyObject* bytes_read = PyObject_CallMethodObjArgs(p->instream,method,bfsize ,NULL); // new ref
			Py_DECREF(bfsize);
			// std::cout << "-------- next 6\n";
			if(PyString_Size(bytes_read) ==0){
				// std::cout << "-------- next 7\n";
				// Raising of standard StopIteration exception with empty value. 
				Py_DECREF(method);
				Py_DECREF(bytes_read);				
				PyErr_SetNone(PyExc_StopIteration);
				// std::cout << "-------- next 7.1\n";
				return NULL;
			}	
			// std::cout << "-------- next 8 "+std::to_string(PyString_Size(bytes_read))+"\n";	 
    		std::string memory(PyString_AsString(bytes_read),PyString_Size(bytes_read));
    		// std::cout << "-------- next 8.1\n";	
    		do_process(memory, *p->pinfo, p->parsers);    		
    		p->rem = PyList_Size(p->pinfo->events);
    		Py_DECREF(bytes_read);
		}
		Py_DECREF(method);
		
		// std::cout << "-------- next 10\n";
	}
	// std::cout << "-------- next 11\n";
	PyObject* event = PyList_GetItem(p->pinfo->events, p->idx);
	Py_INCREF(event);
	p->idx = p->idx +1;
	// std::cout << "-------- next 12 "+std::to_string(p->idx)+"\n";
	return event;		
}


static void
eventstream_dealloc(PyObject* self)
{
    /* We need XDECREF here because when the generator is exhausted,
     * rgstate->sequence is cleared with Py_CLEAR which sets it to NULL.
    */
    // std::cout << "-------- delete\n";
    cunpacker_EventStream *p = (cunpacker_EventStream *)self;
    Py_XDECREF(p->parsers);
    Py_XDECREF(p->instream);
    delete p->pinfo;
    // Py_TYPE(rgstate)->tp_free(rgstate);
}

// eventstream iterator type
static PyTypeObject cunpacker_EventStreamType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "cunpacker._EventStream",            /*tp_name*/
    sizeof(cunpacker_EventStream),       /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)eventstream_dealloc,                         /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER,
      /* tp_flags: Py_TPFLAGS_HAVE_ITER tells python to
         use tp_iter and tp_iternext fields. */
    "Internal eventstream object",           /* tp_doc */
    0,  /* tp_traverse */
    0,  /* tp_clear */
    0,  /* tp_richcompare */
    0,  /* tp_weaklistoffset */
    cunpacker_EventStream_iter,  /* tp_iter: __iter__() method */
    cunpacker_EventStream_next  /* tp_iternext: next() method */
};


PyObject * create_eventstream(PyObject *self, PyObject *args){
  
  	// std::cout << "--------1\n";

  	PyObject* instream;
  	PyObject* parsers;
  	int buffersize;
  	// std::cout << "--------2\n";
  	if (!PyArg_ParseTuple(args, "OiO", &instream, &buffersize, &parsers))  return NULL;

  	/* I don't need python callable __init__() method for this iterator,
     so I'll simply allocate it as PyObject and initialize it by hand. */

	cunpacker_EventStream *p;
	p = PyObject_New(cunpacker_EventStream, &cunpacker_EventStreamType);
	if (!p) return NULL;
	// std::cout << "--------3\n";

	/* I'm not sure if it's strictly necessary. */
	if (!PyObject_Init((PyObject *)p, &cunpacker_EventStreamType)) {
		Py_DECREF(p);
		return NULL;
	}
	// std::cout << "--------4\n";
	Py_INCREF(instream);
	Py_INCREF(parsers);
	// std::cout << "--------4.1\n";
	p->instream = instream;
	// std::cout << "--------4.2\n";
	p->pinfo = new ParserInfo();
	// std::cout << "--------4.3\n";
	p->parsers = parsers;
	// std::cout << "--------4.4\n";
	p->buffersize = buffersize;
	// std::cout << "--------4.5\n";
	p->idx = 0;
	p->rem = 0;
	// std::cout << "--------5\n";

	return (PyObject *)p;
}












PyMODINIT_FUNC
initmpstream_cunpacker(void)
{
    static PyMethodDef FindMethods[] = {
        
        {"process",  process, METH_VARARGS,
            "processes a segment of instream..."}, 
            {"create_eventstream",  create_eventstream, METH_VARARGS,
            "creates a iterator over the stream unpacker functionality based on input stream"},
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


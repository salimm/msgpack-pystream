#include "unpacker.h"
#include "Event.h"
#include <Python.h>
#include <iostream>

ParserInfo convert_parser_info( PyObject *args);
PyObject* convert_pyobject(Event &event);
PyObject* convert_pyobject(ParserInfo &pinfo);
PyObject* convert_pyobject(ParserState &state);
Event& parse_event(PyObject* obj);
ParserState parse_state(PyObject* obj, HeaderUtil &hutil);
PyObject* process(PyObject *self, PyObject *args);


PyObject* process_api_inner(std::string memory, PyObject* piobj, PyObject* deserializers){ 
    Py_INCREF(piobj);
    Py_INCREF(deserializers);
    ParserInfo pinfo = convert_parser_info(piobj);
    do_process(memory, pinfo, deserializers);
    PyObject* result = convert_pyobject(pinfo); 
    Py_DECREF(piobj);
    Py_DECREF(deserializers);
    return result;
}

PyObject* process_api(PyObject *self, PyObject *args){ 
    PyObject* piobj;
    PyObject* deserializers;
    int memsize;
    const char* mem;
    if (!PyArg_ParseTuple(args, "s#OO",  &mem, &memsize, &piobj, &deserializers))
        return NULL;
    ParserInfo pinfo = convert_parser_info(piobj);
    std::string memory(mem,memsize);    
    return process_api_inner(memory, piobj, deserializers);
}


ParserInfo convert_parser_info( PyObject *piobj){
    Py_INCREF(piobj);

    HeaderUtil hutil;
    std::stack<ParserState> stck;
    PyObject* stackobj = PyTuple_GetItem(piobj,0);

    for (long int i =PyList_Size(stackobj)-1; i>-1 ;i--){
        stck.push(parse_state(PyList_GetItem(stackobj, i), hutil));
    }

    int memlen   = int(PyInt_AsLong(PyTuple_GetItem(piobj,7)));
    std::string memory = std::string(PyString_AsString(PyTuple_GetItem(piobj,1)),memlen);
    ScannerState scstate   = static_cast<ScannerState>(int(PyInt_AsLong(PyTuple_GetItem(piobj,2))));
    ParserState state = parse_state(PyTuple_GetItem(piobj,3), hutil);
    int waitingforprop   = int(PyInt_AsLong(PyTuple_GetItem(piobj,5)));
    int parentismap   = int(PyInt_AsLong(PyTuple_GetItem(piobj,6)));
    ParserInfo pinfo = ParserInfo(memory, scstate,state, stck , waitingforprop, parentismap );

    Py_DECREF(piobj);    
    return pinfo;
}


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
    
    PyObject* stck = PyList_New(pinfo.stck.size());        
    int idx = 0;
    while(pinfo.stck.size()!=0){
        PyList_SET_ITEM(stck, idx, convert_pyobject(pinfo.stck.top()));
        pinfo.stck.pop();
        idx++;
    }

    PyObject* state =  convert_pyobject(pinfo.state);

    PyObject* out = Py_BuildValue("(O,s#,i,O,O,i,i)", stck, pinfo.memory.c_str(), pinfo.memory.size(), pinfo.scstate, state, pinfo.events, pinfo.waitingforprop, pinfo.parentismap);
    Py_DECREF(stck);
    Py_DECREF(state);

    return out;
}


PyObject* convert_pyobject(Event &event){
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
    // input output of the original unpacker
    PyObject* events;
    PyObject* memory;
    PyObject* scstate;
    PyObject* state;
    PyObject* stack;
    PyObject* waitingforprop;
    PyObject* parentismap;
} cunpacker_EventStream;


static PyObject* cunpacker_EventStream_iter(PyObject *self){
    Py_INCREF(self);    
    return self;
}

static void print_pointers(cunpacker_EventStream *p){
    std::cout << "\n ++++ stack: "<< p->stack->ob_refcnt <<"\n";
    std::cout << "\n ++++ events: "<< p->events->ob_refcnt <<"\n";
    std::cout << "\n ++++ memory: "<< p->memory->ob_refcnt <<"\n";
    std::cout << "\n ++++ scstate: "<< p->scstate->ob_refcnt <<"\n";
    std::cout << "\n ++++ state: "<< p->state->ob_refcnt <<"\n";
    std::cout << "\n ++++ waitingforprop: "<< p->waitingforprop->ob_refcnt <<"\n";
    std::cout << "\n ++++ parentismap: "<< p->parentismap->ob_refcnt <<"\n";
    std::cout << "\n ++++ parsers: "<< p->parsers->ob_refcnt <<"\n";
    std::cout << "\n ++++ instream: "<< p->instream->ob_refcnt <<"\n";
}

static void set_info_fields(cunpacker_EventStream *p, PyObject* values){
    Py_DECREF(p->stack);
    Py_DECREF(p->events);
    Py_DECREF(p->memory);
    Py_DECREF(p->scstate);
    Py_DECREF(p->state);
    Py_DECREF(p->waitingforprop);
    Py_DECREF(p->parentismap);
    
    // set new values
    p->stack = PyTuple_GetItem(values,0);
    p->memory = PyTuple_GetItem(values,1);
    p->scstate = PyTuple_GetItem(values,2);
    p->state = PyTuple_GetItem(values,3);
    p->events = PyTuple_GetItem(values,4);
    p->waitingforprop = PyTuple_GetItem(values,5);
    p->parentismap = PyTuple_GetItem(values,6);

    Py_INCREF(p->stack);
    Py_INCREF(p->events);
    Py_INCREF(p->memory);
    Py_INCREF(p->scstate);
    Py_INCREF(p->state);
    Py_INCREF(p->waitingforprop);
    Py_INCREF(p->parentismap);
}

static PyObject* pack_process_info(cunpacker_EventStream* p){
    return PyTuple_Pack(8,p->stack, p->memory, p->scstate, p->state, p->events, p->waitingforprop, p->parentismap, PyInt_FromLong(PyString_Size(p->memory)));
}

static PyObject* cunpacker_EventStream_next(PyObject *self){
    cunpacker_EventStream *p = (cunpacker_EventStream *)self;
    if(p->idx >= p->rem){        
        p->rem = 0;
        p->idx = 0;
        while(p->rem==0){
            PyObject* bfsize = PyInt_FromLong(p->buffersize);
            PyObject* method =PyString_FromString("read");       
            PyObject* bytes_read = PyObject_CallMethodObjArgs(p->instream,method,bfsize ,NULL); // new ref            
            Py_DECREF(method);
            Py_DECREF(bfsize);

            if(bytes_read==NULL || PyString_Size(bytes_read) ==0){
                // Raising of standard StopIteration exception with empty value. 
                Py_XDECREF(bytes_read);                  
                PyErr_SetNone(PyExc_StopIteration);
                return NULL;
            }    
            std::string memory = std::string(PyString_AsString(bytes_read),PyString_Size(bytes_read));            
            PyObject* piobj = pack_process_info(p);
            PyObject* result = process_api_inner(memory, piobj, p->parsers);
            Py_DECREF(piobj);
            set_info_fields(p, result);
            Py_DECREF(result);

            p->rem = PyList_Size(p->events);
            Py_DECREF(bytes_read);
        }
    }
    PyObject* event = PyList_GetItem(p->events, p->idx);
    Py_INCREF(event);
    p->idx = p->idx +1;

    return event;        
}


static void eventstream_dealloc(PyObject* self){
    /* We need XDECREF here because when the generator is exhausted,
     * rgstate->sequence is cleared with Py_CLEAR which sets it to NULL.
    */
    cunpacker_EventStream *p = (cunpacker_EventStream *)self;
    Py_XDECREF(p->parsers);
    Py_XDECREF(p->instream);
    Py_XDECREF(p->stack);
    Py_XDECREF(p->events);
    Py_XDECREF(p->memory);
    Py_XDECREF(p->scstate);
    Py_XDECREF(p->state);
    Py_XDECREF(p->waitingforprop);
    Py_XDECREF(p->parentismap);
}

// eventstream iterator type
static PyTypeObject cunpacker_EventStreamType = {
    PyObject_HEAD_INIT(NULL)
    0,                                                         /*ob_size*/
    "cunpacker._EventStream",                                  /*tp_name*/
    sizeof(cunpacker_EventStream),                             /*tp_basicsize*/
    0,                                                         /*tp_itemsize*/
    (destructor)eventstream_dealloc,                           /*tp_dealloc*/
    0,                                                         /*tp_print*/
    0,                                                         /*tp_getattr*/
    0,                                                         /*tp_setattr*/
    0,                                                         /*tp_compare*/
    0,                                                         /*tp_repr*/
    0,                                                         /*tp_as_number*/
    0,                                                         /*tp_as_sequence*/
    0,                                                         /*tp_as_mapping*/
    0,                                                         /*tp_hash */
    0,                                                         /*tp_call*/
    0,                                                         /*tp_str*/
    0,                                                         /*tp_getattro*/
    0,                                                         /*tp_setattro*/
    0,                                                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER,
      /* tp_flags: Py_TPFLAGS_HAVE_ITER tells python to
         use tp_iter and tp_iternext fields. */
    "Internal eventstream object",                             /* tp_doc */
    0,                                                         /* tp_traverse */
    0,                                                         /* tp_clear */
    0,                                                         /* tp_richcompare */
    0,                                                         /* tp_weaklistoffset */
    cunpacker_EventStream_iter,                                /* tp_iter: __iter__() method */
    cunpacker_EventStream_next                                 /* tp_iternext: next() method */
};


PyObject * create_eventstream(PyObject *self, PyObject *args){
  
      PyObject* instream;
      PyObject* parsers;
      int buffersize;

      if (!PyArg_ParseTuple(args, "OiO", &instream, &buffersize, &parsers))  return NULL;
      
    cunpacker_EventStream *p;
    p = PyObject_New(cunpacker_EventStream, &cunpacker_EventStreamType);
    if (!p) return NULL;

    
    if (!PyObject_Init((PyObject *)p, &cunpacker_EventStreamType)) {
        Py_DECREF(p);
        return NULL;
    }


    Py_INCREF(instream);
    Py_INCREF(parsers);
    p->instream = instream;
    p->parsers = parsers;
    p->buffersize = buffersize;
    p->idx = 0;
    p->rem = 0;
    // unpacker objects
    p->events = PyList_New(0);
    p->memory = PyString_FromString("");
    p->scstate = PyInt_FromLong(1);
    Py_INCREF(Py_None);
    p->state = Py_None;
    p->stack = PyList_New(0);
    p->waitingforprop = PyInt_FromLong(0);
    p->parentismap = PyInt_FromLong(0);

    return (PyObject *)p;
}






PyMODINIT_FUNC
initmpstream_cunpacker(void)
{
    static PyMethodDef FindMethods[] = {
        
        {"process",  process_api, METH_VARARGS,
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
    
}


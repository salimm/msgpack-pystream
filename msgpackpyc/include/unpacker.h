#include <iostream>
#include <string>

#include "Format.h"
#include "Event.h"
#include "ScannerState.h"
#include "ParserInfo.h"
#include "HeaderUtil.h"
#include <Python.h>



void do_process(std::string buff, ParserInfo &context);
	
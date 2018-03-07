#include "ParserState.h"

 


ParserState::ParserState(){
    this->formattype = NONE_FRMT;
    Template t;
    this->templatetype = t;
    this->set_length(0);
    this->extcode = 0;
}


ParserState::ParserState(const struct Format &formattype, const struct Template &templatetype, int length, int extcode){
    this->formattype = formattype;
    this->templatetype = templatetype;
    this->set_length(length);
    this->extcode = extcode;
}

ParserState::ParserState(const struct Format &formattype, const struct Template &templatetype, int length, int remaining, int extcode){
    this->formattype = formattype;
    this->templatetype = templatetype;
    this->set_length(length);
    this->remaining = remaining;
    this->extcode = extcode;
}


int ParserState::get_length(){
	return this->length;
}

void ParserState::set_length(int l){
	this->length = l;
	this->remaining = l;
}
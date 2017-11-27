# msgpack-pystream
A SAX-like MessagegPack library in python to deserialize messages from an input stream.

## MessagePack
[MessagePack](http://msgpack.org) is a serializtion/deserialization libary like JSON that uses binary format. Data in message consist of segments. Each segment contain at least 1 byte of header and possible additonal bytes to hold length and value of the data.


## Msgpack-python
The official [u-msgpack-python](https://github.com/vsergeev/u-msgpack-python) library provides a simple to use API to serialize/deserialize objects toand from msgpack binary data. However, this API doesn't provide a stream API that can be used for Big Data. 

## About
This library provides a MessagePack SAX-like API to deserialize msgpack binary data from an input stream. This enables utilization of mssgpack in big data environment. Msgpackstream generates events upon parsing of a binary stream and uppon receiving segments of the data. It does not require the complete data to be ready and exist in memory. As a matter of fact it doesn't require the complete data to be ready at all. It can process existing data and buffer the segments that still require additional bytes to be processed. Futhermore, the library has a easy to read state based and template based implementation that can be easily understood.


## Installation
Msgpackstream can be installed using pip and is supports both python 2.x and 3.x
```bash
    pip install msgpackstream
```

## Usage

Simple msgpackstream usage is to unpack an inputstream

```python
    from msgpackstream.stream import unpack
    ..
    ..
    events = unpack(instream, buffersize)
```
The instream is an inputstream and buffersize is an int value indicating the buffer size to read from the stream. While, the method allows passing the buffersize, this argument is optional and the default value is 1000.

A more flexible way of using msgpackstream is to use the StreamUnpacker class as shown bellow:

```python
    from msgpackstream.stream import StreamUnpacker
    ..
    ..
    unpacker = StreamUnpacker()
    bytes = read()
    while bytes:
        unpacker.process(bytes)
        events = unpacker.generate_events()
        for event in events:
            print(event)                               
    ...
```

Each event is a tuple of 4 different information inspired by [ijson](https://github.com/isagalaev/ijson) JSON library that can be processed as followed additional to using index:

```python
    for prefix, eventtype, formattype, value in events:
        print(eventtype)
```

THe prefix is an array of string indicating the path recursive path to the current segment. For example in a map the prefix will contain the name of the property for the property value segment. Eventtype is an enum contain the type of deserialization event. Formattype, corresponds to the type of  the segment based on the [official documentation](https://github.com/msgpack/msgpack/blob/master/spec.md). Finally value contains the value if the event type is VALUE, MAP_PROPERTY_NAME or EXT. 

## Event Type
Msgpackstream generates various events based on the data being parsed. The different types of events is recorded in an Enum as followed:

```python
class EventType(Enum):
    
    VALUE = 1                   #value event
    ARRAY_START = 2             #event that indicates start of an array
    ARRAY_END = 3               #event that indicates end of an array
    MAP_START = 4               #event that indicates start of a map
    MAP_END = 5                 #event that indicates end of a map
    MAP_PROPERTY_NAME = 6       #event that indicates property name
    EXT = 7                     #event that indicates ext value
```

## FormatType
Currently, msgpackstream supports all format types in msgpack official specification as of Sep 18 2017:

```python
   class FormatType(Enum):
    
    POS_FIXINT = Format(0x00 , 0x80) #(formatcode, mask)
    NEG_FIXINT = Format(0xE0 , 0xE0)
    
    FIXMAP = Format(0x80 , 0xF0)
    FIXARRAY = Format(0x90 , 0xF0)
    FIXSTR = Format(0xA0 , 0xE0)
    
    NIL = Format(0xC0 , 0xFF)
    NEVER_USED = Format(0xC1 , 0xFF)
    
    FALSE = Format(0xC2 , 0xFF)
    TRUE = Format(0xC3 , 0xFF)
    
    BIN_8 = Format(0xC4 , 0xFF)
    BIN_16 = Format(0xC5 , 0xFF)
    BIN_32 = Format(0xC6 , 0xFF)
    
    EXT_8 = Format(0xC7 , 0xFF)
    EXT_16 = Format(0xC8 , 0xFF)
    EXT_32 = Format(0xC9 , 0xFF)
    
    
    FLOAT_32 = Format(0xCA , 0xFF)
    FLOAT_64 = Format(0xCB , 0xFF)
    
    UINT_8 = Format(0xCC , 0xFF)
    UINT_16 = Format(0xCD , 0xFF)
    UINT_32 = Format(0xCE , 0xFF)
    UINT_64 = Format(0xCF , 0xFF)
    
    INT_8 = Format(0xD0 , 0xFF)
    INT_16 = Format(0xD1 , 0xFF)
    INT_32 = Format(0xD2 , 0xFF)
    INT_64 = Format(0xD3 , 0xFF)
    
    FIXEXT_1 = Format(0xD4 , 0xFF)
    FIXEXT_2 = Format(0xD5 , 0xFF)
    FIXEXT_4 = Format(0xD6 , 0xFF)
    FIXEXT_8 = Format(0xD7 , 0xFF)
    FIXEXT_16 = Format(0xD8 , 0xFF)
    
    STR_8 = Format(0xD9 , 0xFF)
    STR_16 = Format(0xDA , 0xFF)
    STR_32 = Format(0xDB , 0xFF)
    
    ARRAY_16 = Format(0xDC , 0xFF)
    ARRAY_32 = Format(0xDD , 0xFF)
    
    MAP_16 = Format(0xDE , 0xFF)
    MAP_32 = Format(0xDF , 0xFF)
```


However, if event type is EXT, the formattype will be an instance of the class ExtType to hold and additional ext code indicating the type of the extension:

```python
class ExtType():
    '''
    Class for Extention Type including format type, template and length in the header
    '''
    
    def __init__(self, formattype, extcode):
        self._formattype = formattype
        self._extcode = extcode
        
    ...
    ...
    
    formattype = property(get_formattype, set_formattype)
    extcode = property(get_extcode, set_extcode)
    
```

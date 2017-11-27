# msgpack-pystream
A SAX-like MessagegPack library in python to deserialize messages from an input stream.

## MessagePack
[MessagePack](http://msgpack.org) is a serializtion/deserialization libary like JSON that uses binary format. Data in message consist of segments. Each segment contain at least 1 byte of header and possible additonal bytes to hold length and value of the data.


## MsgPack-python
The official [msgpack-python](https://github.com/msgpack/msgpack-python) library provides a simple to use API to serialize/deserialize objects toand from msgpack binary data. However, this API doesn't provide a stream API that can be used for Big Data. 

## About
This library provides a MessagePack SAX-like API to deserialize msgpack binary data from an input stream. This enables utilization of mssgpack in big data environment. Msgpackstream generates events upon parsing of a binary stream and uppon receiving segments of the data. It does not require the complete data to be ready and exist in memory. As a matter of fact it doesn't require the complete data to be ready at all. It can process existing data and buffer the segments that still require additional bytes to be processed. Futhermore, the library has a easy to read state based and template based implementation that can be easily understood.

## Events
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

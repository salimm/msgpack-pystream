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

For more details and working examples read [here](https://github.com/salimm/msgpack-pystream/wiki/Installation-and-Usage)

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
Currently, msgpackstream supports all format types in msgpack official specification as of Sep 18 2017. The full list can be found [here](https://github.com/salimm/msgpack-pystream/wiki/Format-Types)


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

# Extension Type
Msgpackstream allows handling of extension types in two different ways:

- Receiving a byte[] within and EXT event that can be processed
- Registering a custom ExtParser class that can be used to parse the byte[] within the buffer

The latter is slightly more efficient as it prevents an extra step of copying byte[] into an event

```python
class   ExtTypeParser():
    __metaclass__ = ABCMeta
    
        
    @abstractmethod
    def deserialize(self, exttype, buff, start , end):
        '''
            Should be implemented for every user defined extension type
        :param data:
        '''
    @abstractmethod
    def handled_extcode(self):
        pass
```

The handled_extcode class should simply return the extcode number that is handled by the parser implmentation. However, the main method is the deserialize method that received exttype as explained in the previous section, buffer and the range that value can be found in. Finally an instance of the ExtTypeParser can be registered using the following methods:

```python
    parser = MyExtParser()
    unpacker = StreamUnpacker()
    unpacker.register(parser)
```

or 

```python
    parser = MyExtParser()
    unpack(instream, buffersize, [praser])
```

## TODO

- Optimize byte scanner
- Add additional unit test for more complecated messages


## Related Projects and Links
- Check out my parallel project to create some sort of easy to use Python Object Parser ([POP](https://github.com/salimm/pop))
- Check out official msgpack package [u-msgpack-python](https://github.com/vsergeev/u-msgpack-python)
- Another third msgpack package for python [msgpack-python](https://github.com/msgpack/msgpack-python)
- Latest msgpack specification [link](https://github.com/msgpack/msgpack/blob/master/spec.md)

## Credits:
Thanks to everyone who contributed to the [msgpack](). Additionaly the interface of the api was inspired by the simple interface of [ijson](https://github.com/isagalaev/ijson) library.

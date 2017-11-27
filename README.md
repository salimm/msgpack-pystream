# msgpack-pystream
A SAX-like MessagegPack library in python to deserialize messages from an input stream.

## MessagePack
[MessagePack](http://msgpack.org) is a serializtion/deserialization libary like JSON that uses binary format. Data in message consist of segments. Each segment contain at least 1 byte of header and possible additonal bytes to hold length and value of the data.


## MsgPack-python
The official [msgpack-python](https://github.com/msgpack/msgpack-python) library provides a simple to use API to serialize/deserialize objects toand from msgpack binary data. However, this API doesn't provide a stream API that can be used for Big Data. 

## About
This library provides a MessagePack SAX-like API to deserialize msgpack binary data from an input stream. This enables utilization of mssgpack in big data environment. Msgpackstream generates events upon parsing of a binary stream and uppon receiving segments of the data. It does not require the complete data to be ready and exist in memory. As a matter of fact it doesn't require the complete data to be ready at all. It can process existing data and buffer the segments that still require additional bytes to be processed. Futhermore, the library has a easy to read state based implementation that can be easily understood.

## Events
Msgpackstream generates various events based on the data being parsed. The different types of events is recorded in an Enum as followed:

```python
class  ScannerState(Enum):
    '''
        Scanner state contains the intention of the scanner and what it expects next based on what it has read so far
    '''
    IDLE = 1 
    WAITING_FOR_HEADER = 2
    WAITING_FOR_EXT_TYPE = 3
    WAITING_FOR_LENGTH = 4
    WAITING_FOR_VALUE = 5
    SEGMENT_ENDED = 6
```

# msgpack-pystream
A SAX-like MessagegPack library in python to deserialize messages from an input stream.

## MessagePack
[MessagePack](http://msgpack.org) is a serializtion/deserialization libary like JSON that uses binary format. Data in message consist of segments. Each segment contain at least 1 byte of header and possible additonal bytes to hold length and value of the data.

'''
Created on Nov 14, 2017

@author: Salim
'''
from _io import BytesIO, StringIO
import msgpack
from msgpackstream import StreamUnpacker
import ijson
import json



idx = 2

# f = open("../sample"+str(idx)+".msgpck","rb")
     
    
# bdata =  msgpack.packb({"test":1})
s = ""
for i in range(1):
    s = s + "salam salam salam salam salam salam" 

a = []
for i in range(2):
    a.append([1.2, 21232213121, 3, [2, "as", {"field": [1, 2]}]])
a2 = []
for i in range(20000):
    a2 = a2 + [1]
    
m2 = {}
for i in range(2000):
    m2['field' + str(i)] = i
    
m = {"f1":s, "f2":a}

buf = StringIO()
buf.write(json.dumps(m).decode('ascii'))
buf.seek(0)
parser = ijson.parse(buf)

for prefix, event, value in parser:
    print((prefix, event, value))


bdata = msgpack.packb(None)
 
buf = BytesIO()
buf.write(bdata)
buf.seek(0)

unpacker = StreamUnpacker();
try:
    bytes_read = buf.read(10)
    while bytes_read:
        unpacker.process(bytes_read)
        for e in unpacker.generate_events():
            print(e)
        bytes_read = buf.read(10)        
finally:
    buf.close()

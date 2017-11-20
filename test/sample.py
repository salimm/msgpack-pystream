'''
Created on Nov 14, 2017

@author: Salim
'''
from _io import BytesIO
import msgpack
from msgpackstream.stream import StreamUnpacker

idx = 2

# f = open("../sample"+str(idx)+".msgpck","rb")
     
    
# bdata =  msgpack.packb({"test":1})
s = ""
for i in range(10):
    s = s + "salam salam salam salam salam salam" 

a= []
for i in range(100):
    a.append(i)
bdata =  msgpack.packb(a)
# f.close()
 
buf = BytesIO()
buf.write(bdata)
buf.seek(0)

unpacker= StreamUnpacker();
try:
    bytes_read = buf.read(10)
    while bytes_read:
        unpacker.process(bytes_read)
        for e in unpacker.generate_events():
            print(e)
        bytes_read = buf.read(10)        
finally:
    buf.close()
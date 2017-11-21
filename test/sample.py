'''
Created on Nov 14, 2017

@author: Salim
'''
from _io import BytesIO, StringIO
import msgpack
import ijson
import json
import msgpackstream
import math



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

a = []
for i in range(int(math.pow(2, 1))):
    a.append(b'')

buf = StringIO()
buf.write(json.dumps([1]).decode('ascii'))
buf.seek(0)
parser = ijson.parse(buf)

for prefix, event, value in parser:
    print((prefix, event, value))


bdata = msgpack.packb(a)
print(bdata) 
buf = BytesIO()
buf.write(b'\xd4\x01\x00')
buf.seek(0)

for e in msgpackstream.stream_unpack(buf):
    print(e)

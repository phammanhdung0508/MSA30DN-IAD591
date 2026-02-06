import struct
data=open("srmodels/srmodels.bin","rb").read()
n=struct.unpack_from("<I",data,0)[0]
o=4; names=[]
for _ in range(n):
    name=data[o:o+32].split(b'\x00',1)[0].decode()
    o+=32
    file_num=struct.unpack_from("<I",data,o)[0]; o+=4
    names.append(name)
    o += file_num*(32+4+4)
print("models:", names)

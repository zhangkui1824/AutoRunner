import gzip
import base64

def depack(a):
    # 一开始爬取用，现在没用了
    b = base64.b64decode(a)
    c = gzip.decompress(b).decode("utf-8")
    return c


s="""NmMNCh+LCAAAAAAAAAOrVkrOT0lVsjLUUcpNLS5OTAeylZ51THjaNV9JR6kotbg0p0TJqlopMSUlJDMXKGmgo5RakZgblJqTWJKZn+eaBxU3NDM2s7Q0tDQxAAKIGkc0PRADjAxqawGUAC+CdgAAAA0KMA0KDQo="""
#r=depack(s)
a=base64.b64decode(s)
#b=a.decode('ascii')
#c=depack(s)
print(a)
b="""b'6c\r\n\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x03\xabVJ\xceOIU\xb22\xd4Q\xcaM-.NL\x07\xb2\x95\x9euLx\xda5_IG\xa9(\xb5\xb84\xa7D\xc9\xaaZ)1%%$3\x17(i\xa0\xa3\x94Z\x91\x98\x1b\x94\x9a\x93X\x92\x99\x9f\xe7\x9a\x07\x157436\xb3\xb44\xb441\x00\x02\x88\x1aG4=\x10\x03\x8c\x0cjk\x01\x94\x00/\x82v\x00\x00\x00\r\n0\r\n\r\n'
"""
c=gzip.decompress(b).decode()
print(c)
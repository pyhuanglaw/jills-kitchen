"""Find Simplified Chinese characters: every CJK character that ICU's Hans-Hant transform changes (via the system
libicu, no network). Review each hit — some are valid Traditional forms (沉, 干貝, 宿舍, 占).
Usage: python3 tools/hans_scan.py FILE...   (docs/RELEASE_CHECKLIST.md §4)"""
import ctypes, sys, re
V='74'
i18n=ctypes.CDLL(f'libicui18n.so.{V}')
openU=getattr(i18n,f'utrans_openU_{V}'); trans=getattr(i18n,f'utrans_transUChars_{V}')
openU.restype=ctypes.c_void_p
def u16(s):
    b=s.encode('utf-16-le'); n=len(b)//2
    arr=(ctypes.c_uint16*(n*4+16))(); ctypes.memmove(arr,b,len(b)); return arr,n
tid,tn=u16('Hans-Hant'); err=ctypes.c_int(0)
T=openU(tid,tn,0,None,0,None,ctypes.byref(err))
assert err.value<=0 and T, ('open',err.value)
def conv(s):
    arr,n=u16(s); ln=ctypes.c_int32(n); lim=ctypes.c_int32(n); e=ctypes.c_int(0)
    trans(ctypes.c_void_p(T),arr,ctypes.byref(ln),ctypes.c_int32(len(arr)),ctypes.c_int32(0),ctypes.byref(lim),ctypes.byref(e))
    return bytes(arr)[:ln.value*2].decode('utf-16-le')
cjk=re.compile(r'[一-鿿]')
hits={}
for f in sys.argv[1:]:
    for ln,line in enumerate(open(f,encoding='utf-8'),1):
        for ch in set(cjk.findall(line)):
            t=conv(ch)
            if t!=ch: hits.setdefault((ch,t),[]).append(f'{f.split("/")[-1]}:{ln}')
for (ch,t),where in sorted(hits.items(),key=lambda x:-len(x[1])):
    print(ch,'→',t,len(where),where[:4])
print('distinct suspicious:',len(hits))

#!/usr/bin/env python3
import sys,fileinput,re,hashlib,functools
#[sys.stdout.write(re.sub("[A-Z][0-9]{2}[A-Z]",lambda s:hashlib.sha1(s.group(0)).hexdigest(),l))for l in fileinput.input()]

cachelimit = 50000

colorrange=list(range(1,6+1)) + list(range(9,15+1)) + list(range(17,230+1))

premap = {u"fletcher2":  88,
          u"fletcher4": 112,
          u"sha256"   :  12,
          u"sha512"   : 115,
          u"uncompressed": 202,
          u"lz4": 190,
          u"contiguous": 99,
          u"unencrypted": 118,
          u"encrypted":   93,
          u"LE":		 2,
          u"BE":	       177,
          u"unique":	 154,
          u"double":	 162,
          u"L0":		 21,
          u"L1":		 3,
          u"L2":		197,
          u"ZFS plain file": 32,
          u"single": 1,
          u"double": 2,
          u"gzip-\d": 123,}

def cachehash(input):
    matched = False
    for key in premap.keys():
      if re.match(key,input):
        out = premap[key]
        input = input.encode('utf-8')
        matched = True
        break
    if not matched: 
      input = input.encode('utf-8')
      out = colorrange[int("0x" + str(hashlib.sha1(input).hexdigest()),16) % len(colorrange)]
#    print("DEBUG: INPUT={} OUTPUT={} HASHOUT={} ISIN={}".format(input,out,colorrange[int("0x" + str(hashlib.sha1(input).hexdigest()),16) % len(colorrange)],str(input) in premap.keys()))
    return out

@functools.lru_cache(maxsize=cachelimit)
def colorwrap(text,forcecolor=None):
#  print("NUDEBUG: INPUT={}".format(text))
  if forcecolor is not None:
    colorwith=str(int(forcecolor))
  else:
    colorwith=str(cachehash(text))
  return str('\033[38;5;' + colorwith + 'm' + text + '\033[0m')

#print(colorrange)
for line in fileinput.input():
    for predef in premap.keys():
      line = re.sub(r"(\W+)({})".format(predef),lambda s:'{}{}'.format(s.group(1),colorwrap(s.group(2))),line)
#    lambda s: "DVA[%s]=<%s:%s:%s>".format(colorwrap(s.group(0),cachehash(s.group(0))),colorwrap(s.group(1),cachehash(s.group(1))),colorwrap(s.group(2),cachehash(s.group(2))),colorwrap(s.group(3),cachehash(s.group(3)))
    line = re.sub(r"DVA\[(\d)\]=<(\d):([0-9a-f]+):([0-9a-f]+)>",lambda s: "DVA[" + colorwrap(s.group(1)) +"]=<"+colorwrap(s.group(2))+":"+colorwrap(s.group(3))+":"+colorwrap(s.group(4))+">",line)
    line = re.sub(r"(size|birth)=([0-9a-f]+)L/([0-9a-f]+)P",lambda s: "{}={}L/{}P".format(s.group(1),colorwrap(s.group(2)),colorwrap(s.group(3))),line)
    line = re.sub(r"(size|birth)=([0-9a-f]+)L",lambda s: "{}={}L".format(s.group(1),colorwrap(s.group(2))),line)
    line = re.sub(r"cksum=([0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+)",lambda s: "cksum={}".format(colorwrap(s.group(1),int("0x"+str(s.group(1).replace(":","")),16) % len(colorrange))),line)
    line = re.sub(r"\A(\W+)([0-9a-f]+)(\W)",lambda s: "{}{}{}".format(s.group(1),colorwrap(s.group(2)),s.group(3)),line)
    #line = re.sub(" fletcher4",' ' + colorwrap("fletcher4",cachehash("fletcher4")),line)
    print(line,end="")


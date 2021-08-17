#!/usr/bin/env python3
import sys,fileinput,re,hashlib,functools
from math import log,sqrt
#[sys.stdout.write(re.sub("[A-Z][0-9]{2}[A-Z]",lambda s:hashlib.sha1(s.group(0)).hexdigest(),l))for l in fileinput.input()]

cachelimit = 10000

colorrange=list(range(1,6+1)) + list(range(9,15+1)) + list(range(17,230+1))
bytescale=[160,196,9,202,208,214,220,226,190,154,118,82,46,48,50,45,33,21,57,93,129,165,201]

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


@functools.lru_cache(maxsize=cachelimit)
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

def genericcolor(text):
  return colorwrap(text)

def pathcolor(text):
  res = []
  for s in re.split("/",text):
    tmp = s.split("@")
    out = colorwrap(tmp[0])
    if len(tmp) == 2:
      out += "@" + colorwrap(tmp[1])
    res.append(out)
  return "/".join(res)

def ratiocolor(text):
  bits = re.fullmatch(r"\A([0-9\.]+)(x)\Z",text)
#  print("\nDEBUG SIZECOL: {} {}".format(text,bits.groups()))
#  hashcol = bytescale[int((float(bits.group(1)) / 1024.) * len(bytescale)-1)]
#  hashcol = bytescale[int((log(float(bits.group(1))) / log(1024.)) * len(bytescale)-1)]
  val = sqrt(float(bits.group(1)) - 1.0) / sqrt(4.0)
#  print("\nDEBUG SIZECOL VAL: {}".format(val))
  if val >= 1.0:
    val = 1.0
  hashcol = bytescale[int(val * (len(bytescale)-1))]
#  print("\nDEBUG SIZECOLOR: {} {} {} {} {}".format(text,hashcol,bits.group(1),bits.group(2),val))
  return colorwrap(bits.group(1),forcecolor=hashcol) + colorwrap(bits.group(2))

def sizecolor(text):
  bits = re.fullmatch(r"\A([0-9\.]+)([A-Z])?\Z",text)
  if bits is None:
    return colorwrap(text)
#  print("\nDEBUG SIZECOL: {} {}".format(text,bits.groups()))
#  hashcol = bytescale[int((float(bits.group(1)) / 1024.) * len(bytescale)-1)]
#  hashcol = bytescale[int((log(float(bits.group(1))) / log(1024.)) * len(bytescale)-1)]
  hashcol = bytescale[int((sqrt(float(bits.group(1))) / sqrt(1024)) * len(bytescale)-1)]
  out = colorwrap(bits.group(1),forcecolor=hashcol)
  if len(bits.groups()) == 2 and bits.group(2) is not None:
    out += colorwrap(bits.group(2))
#  print("\nDEBUG SIZECOLOR: {} {} {}".format(text,hashcol,bits.group(1),bits.group(2)))
  return out

firstline = True
globalgeneric = False
generichash = False
cols_inuse = []
knowncols = {u"NAME": pathcolor,
             u"MOUNTPOINT": pathcolor,
             u"AVAIL": sizecolor,
             u"USED": sizecolor,
             u"REFER": sizecolor,
             u"USEDSNAP": sizecolor,
             u"USEDDS": sizecolor,
             u"USEDCHILD": sizecolor,
             u"LUSED": sizecolor,
             u"LREFER": sizecolor,
             u"WRITTEN": sizecolor,
             u"RATIO":ratiocolor,
             u"REFRATIO":ratiocolor,
            }

for entry in bytescale:
  print("{} ".format(colorwrap(str(entry),forcecolor=entry)),end="")
print("")

for line in fileinput.input():
#    print(line)
    if firstline:
      if not re.fullmatch("\A[\sA-Z0-9_]+\Z",line):
        print(colorwrap("WARNING: column header not detected, running in generic mode...",forcecolor="8"))
        generichash = True
        globalgeneric = True
      else:
        cols = re.split("\s\s+",line)
        for col in cols:
          try:
            cols_inuse.append(knowncols[col.strip()])
          except KeyError:
            cols_inuse.append(genericcolor)
#            print("DEBUG COLUMN FUNC: UNKNOWN COL {}".format(col))
#          print("DEBUG COLUMN: {} {}".format(col,cols_inuse))
#        continue
    cols = re.split("\s\s+",line)
    whitesp = [""] + re.findall(r"(\s\s+)",line)
    if not generichash and len(cols) != len(cols_inuse):
      print("Warning: splitter error, switching to generic hash for this line...")
      #cols = line.split()
      generichash = True
    dbgstr = ""
#    print("DEBUG LINECNT: {} {} {} {}".format(len(cols),len(whitesp),cols,whitesp))
    for colN in range(len(cols)):
      if firstline:
        # FIXME: make it just print bold
        colorfunc = genericcolor
      elif not generichash:
        colorfunc = cols_inuse[colN]
      else:
        colorfunc = genericcolor
#      dbgstr += "DEBUG: A{}AB{}B".format(whitesp[colN],colorfunc(cols[colN]))
      print("{}{}".format(whitesp[colN],colorfunc(cols[colN].strip())),end="")
    print("")
#    print(dbgstr)
    if not globalgeneric:
      generichash = False
    firstline = False

#!/usr/bin/env python3
import sys,fileinput,re,hashlib,functools,shutil,os
from math import log,sqrt
#[sys.stdout.write(re.sub("[A-Z][0-9]{2}[A-Z]",lambda s:hashlib.sha1(s.group(0)).hexdigest(),l))for l in fileinput.input()]


cachelimit = 10000

colorrange=list(range(1,6+1)) + list(range(9,15+1)) + list(range(19,230+1))
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
          u"gzip-\d": 123,
          u"disabled": 160,}

CLREOL=u"\x1B[K"

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
  return str('\033[38;5;' + colorwith + 'm' + text + '\033[39m')

def genericcolor(text):
  return colorwrap(text)

def pathcolor(text):
  res = []
  out = ""
  for s in re.split("/",text):
    for divider in ["@","#"]:
      tmp = s.split(divider)
      out = colorwrap(tmp[0])
      if len(tmp) == 2:
        out += divider + colorwrap(tmp[1])
        break
    res.append(out)
  return "/".join(res)

def ratiocolor(text):
  bits = re.fullmatch(r"\A([0-9\.]+)(x?)\Z",text)
  suf = ""
  ret = ""
  hashcol = 0
#  print("\nDEBUG SIZECOL: {} {}".format(text,bits.groups()))
#  hashcol = bytescale[int((float(bits.group(1)) / 1024.) * len(bytescale)-1)]
#  hashcol = bytescale[int((log(float(bits.group(1))) / log(1024.)) * len(bytescale)-1)]
  try:
    val = sqrt(float(bits.group(1)) - 1.0) / sqrt(4.0)
#  print("\nDEBUG SIZECOL VAL: {}".format(val))
    if val >= 1.0:
      val = 1.0
    hashcol = bytescale[int(val * (len(bytescale)-1))]
#  print("\nDEBUG SIZECOLOR: {} {} {} {} {}".format(text,hashcol,bits.group(1),bits.group(2),val))
    if (bits.group(2) is not None):
      suf = bits.group(2)
    ret = colorwrap(bits.group(1),forcecolor=hashcol) + colorwrap(suf)
  except:
    ret = colorwrap(text)
  return ret

def sizecolor(text):
  bits = re.fullmatch(r"\A([0-9\.]+)([A-Z])?\Z",text)
  if bits is None:
    return colorwrap(text)
#  print("\nDEBUG SIZECOL: {} {}".format(text,bits.groups()))
#  hashcol = bytescale[int((float(bits.group(1)) / 1024.) * len(bytescale)-1)]
#  hashcol = bytescale[int((log(float(bits.group(1))) / log(1024.)) * len(bytescale)-1)]
#  print("DBG int((sqrt(float(bits.group(1))) / sqrt(1024)) * len(bytescale)-1) = {}".format(int((sqrt(float(bits.group(1))) / sqrt(1024)) * len(bytescale)-1)))
  # blasted -p
#  if bits.group(2) is not None or int(bits.group(1)) <= 1024:
#    hashcol = bytescale[int((sqrt(float(bits.group(1))) / sqrt(1024)) * len(bytescale)-1)]
#  else:
  val = float(bits.group(1))
  while val > 1024.0:
    val = val / 1000.0
#  print("DBG: {} {} {}".format(text,bits.group(1),val))
  hashcol = bytescale[int((sqrt(val) / sqrt(1024)) * len(bytescale)-1)]

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

#for entry in bytescale:
#  print("{} ".format(colorwrap(str(entry),forcecolor=entry)),end="")
#print("")

def linecolor(n=0):
  ret = "\033[48;5;233m"
  if (n % 2) == 0:
    ret = "\033[49m"
  return ret

COLUMNS = shutil.get_terminal_size()[0]

#DELIMITER=""
#for i in range(COLUMNS):
#  print("{} {}".format(str(i % 10),str(int(i / 10))))
#  DELIMITER += colorwrap(str((i+1) % 10),forcecolor=cachehash(str(int(i / 10))))
  
linenum=0
for line in fileinput.input():
    charlength = 0
#    print(line)
    if firstline:
      if not re.fullmatch("\A[\sA-Z0-9_\-\:\.]+\Z",line):
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
    whitesp = [linecolor(linenum)] + re.findall(r"(\s\s+)",line)
    if not generichash and len(cols) != len(cols_inuse):
      print("Warning: splitter error, switching to generic hash for this line...")
      #cols = line.split()
      generichash = True
    dbgstr = ""
#    print("DEBUG LINECNT: {} {} {} {}".format(len(cols),len(whitesp),cols,whitesp))
    wht = 0
    wholestr = ""
    plainstr = ""
    debugstr = ""
    debugstr2 = ""
    colmul=0
    for colN in range(len(cols)):
      if firstline:
        # FIXME: make it just print bold
        colorfunc = genericcolor
      elif not generichash:
        colorfunc = cols_inuse[colN]
      else:
        colorfunc = genericcolor
#      dbgstr += "DEBUG: A{}AB{}B".format(whitesp[colN],colorfunc(cols[colN]))
      wip = cols[colN].replace("\n","").expandtabs()
      # we shoved the leading line color in here
      if (colN == 0):
        plainws = ""
      else:
        plainws = whitesp[colN].expandtabs()
      ws_wip = whitesp[colN].expandtabs()
#      print("W" + str(len(whitesp[colN])) + "X" + ws_wip + "Y" + str(len(ws_wip)) + "Z")
#      print(ws_wip.encode("utf-8")[1:])
#      print("X" + "{}".format(ws_wip) + "Y" + str(len("{}".format(ws_wip))) + "Z")
      plainstr += plainws + wip
      wholestr += "{}{}".format(ws_wip,colorfunc(wip))
      wht += len(plainws + wip)
      debugstr2 += " " + str(len(ws_wip)) + " " + str(len(wip))
      if (len(plainws) > 0):
        debugstr += (" " * (len(plainws)-1)) + "1"
      if (len(wip) > 0):
        debugstr += (" " * (len(wip)-1)) + "2"
#      print("DEBUG: len(ln)={} len(wht)={} COLUMNS={}".format(len(ln),wht,COLUMNS))
#      print(ln, end="")# + (" " * wht),end="")
#    if (linenum > 1):
#      print(CLREOL + "BEES")
#    else:
#    try:
#      envc = os.environ["COLUMNS"]
#    except:
#      envc = -1
#    print("\nDEBUG: wht={} COLUMNS={} env[COLUMNS]=={} len(COLUMNS-wht)={}\n".format(wht,COLUMNS,envc,len(" " * (COLUMNS - (wht % COLUMNS)))),end="")
#    print(" " * (COLUMNS - (wht % COLUMNS)))
    try:
      MYC=os.environ["MYCOLUMNS"]
    except:
      MYC=-1
    try:
      COLS =os.environ["COLUMNS"]
    except:
      COLS=-1
#    print(DELIMITER)
    tmppad=""
    while (colmul < len(plainstr)):
      colmul += COLUMNS
#    print("DEBUG: len(plainstr)={} len(wholestr)={} wht={} EVILCOLUMNS={} COLUMNS={} GETCOLUMNS={} MYC={} DIFF={}".format(len(plainstr),len(wholestr),wht,os.get_terminal_size(2)[0],COLS,shutil.get_terminal_size()[0],MYC,colmul-wht))
#    print(debugstr2)
#    print(debugstr,end="")
    tmppad = " "*(colmul-wht)
#    if len(tmppad) > 0:
#      print(tmppad[:-1] + "3")
#    print(plainstr)
    print(wholestr,end="")
    print(tmppad,end="")
    print("\033[49m",end="")
    print("")
#    print(dbgstr)
    if not globalgeneric:
      generichash = False
    firstline = False
    linenum = (linenum+1) % 4

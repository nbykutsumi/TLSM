from numpy import *
from datetime import datetime, timedelta
from collections import deque
import myfunc.IO.GRDC as GRDC
import myfunc.util as util
import calendar
import os

#lSite = ["Datong","Bahadurabad","Vicksburg","StungTreng","Obidos"]
#lSite = ["Bahadurabad"]
#lSite = ["Datong"]
#dID   = {"Thebes":6742201
#        ,"Datong":2181900
#        ,"Bahadurabad":2651100
#        ,"Vicksburg":4127800
#        ,"StungTreng":2569005
#        ,"Obidos":3629000
#        }
#
#dArea = {"Thebes":-9999.
#        ,"Datong":1705383
#        ,"Bahadurabad":636130
#        ,"Vicksburg":2964255
#        ,"StungTreng":635000
#        ,"Obidos":4680000
#        } # [m^2]

#--- load GRDC list -----
crd      = "np"
res      = "one"
grdc     = GRDC.GRDC()
mygrdc   = grdc.loadMyList(crd=crd, res=res)
dArea    = mygrdc.dArea
#--- make targed stnID list --
#f = open("/tank/utsumi/data/TLSM/GRDC_Station/Target.over10yr100000km2.csv","r")
f = open("/tank/utsumi/data/TLSM/GRDC_Station/TargetStations.np.one.Aft1993.100000km2.csv","r")
lines = f.readlines()
f.close()
lstnID  = []
for i, sline in enumerate(lines[1:]):
  line  = sline.split(",")
  lstnID.append(int(line[5]))
#------------------------------

#lstnID = [4356100]

miss_out = -9999.
#ntag = 5
#oBaseDir = "/tank/utsumi/H08/out/TAGFLW/%02dc"%(ntag)
oBaseDir = "/tank/utsumi/out/GRDC"
lnoexist = []
for stnID in lstnID:
  srcDir  = "/data1/hjkim/Dis/GRDC/daily"
  srcDir0 = "/data1/hjkim/Dis/GRDC/daily.option00"
  srcDir1 = "/data1/hjkim/Dis/GRDC/daily.option01"
  srcDir2 = "/data1/hjkim/Dis/GRDC/daily.option02"
  for DIR in [srcDir, srcDir0, srcDir1, srcDir2]:
    srcPath = DIR + "/%s.day"%(stnID)
    if os.path.exists(srcPath):
      break

  #---------
  try:
    f=open(srcPath, "r")
  except IOError:
    lnoexist.append(stnID)
    continue

  #---------
  lines = f.readlines()
  for i,line in enumerate(lines):
    if line[:10]=="YYYY-MM-DD":
      linesBody = lines[i+1:]
      break

  #-- prep ---
  line = linesBody[0].split(";")
  DATE = line[0]
  YearNow = int(DATE[:4])
  MonNow  = int(DATE[5:7])

  dDaily  = {}
  lKey    = []
  for iline, line in enumerate(linesBody):
    line = line.split(";")
    DATE = line[0]
    Year = int(DATE[:4])
    Mon  = int(DATE[5:7])
    Day  = int(DATE[8:10])
    Key  = (Year,Mon)
    v    = float(line[3])

    if dDaily.has_key(Key):
      dDaily[Key].append(v)
    else:
      print Year,Mon
      dDaily[Key] = deque([v])
      lKey.append(Key)

  lout =[]
  for Key in lKey:  # <-- Do not use "dDaily.keys()". It returnes un-sorted list of keys

    #coef = 60*60*24./ dArea[Site] / 1.0e+3  # m3/s --> mm/m2
    #mv   = ma.masked_less( array(dDaily[Key]), 0.0).sum() * coef  # mm/m^2/month

    a1tmp = array(dDaily[Key])
    mv = ma.masked_less(a1tmp , 0.0).mean()   # m^3/s
    mv = float(mv)
    #------
    if isnan(mv):
      mv = miss_out
    #------
    Year, Mon = Key
    lout.append([Year,Mon,mv])
  #-- save ----------------
  ocsv  = util.list2csv(lout)
  oDir  = oBaseDir + "/Monthly"
  oPath = oDir + "/%s.csv"%(stnID)
  util.mk_dir(oDir)
  f=open(oPath,"w"); f.write(ocsv); f.close()
  print oPath

#--- write noexist -----
snoexist = "\n".join( map(str, lnoexist) ).strip()
f = open("/tank/utsumi/data/TLSM/GRDC_Station/noexist.csv","w")
f.write(snoexist)
f.close()


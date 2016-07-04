from numpy import *
from datetime import datetime, timedelta
import myfunc.util as util
from collections import deque
import calendar
import os

#lSite = ["Datong","Bahadurabad","Vicksburg","StungTreng","Obidos"]
#lSite = ["Bahadurabad"]
lSite = ["Datong"]
dID   = {"Thebes":6742201
        ,"Datong":2181900
        ,"Bahadurabad":2651100
        ,"Vicksburg":4127800
        ,"StungTreng":2569005
        ,"Obidos":3629000
        }

dAra  = {"Thebes":-9999.
        ,"Datong":1705383
        ,"Bahadurabad":636130
        ,"Vicksburg":2964255
        ,"StungTreng":635000
        ,"Obidos":4680000
        } # [m^2]


miss_out = -9999.
#ntag = 5
#oBaseDir = "/tank/utsumi/H08/out/TAGFLW/%02dc"%(ntag)
oBaseDir = "/tank/utsumi/out/GRDC"
for Site in lSite:
  ID      = dID[Site]
  srcDir  = "/data1/hjkim/Dis/GRDC/daily"
  srcDir0 = "/data1/hjkim/Dis/GRDC/daily.option00"
  srcDir1 = "/data1/hjkim/Dis/GRDC/daily.option01"
  srcDir2 = "/data1/hjkim/Dis/GRDC/daily.option02"
  for DIR in [srcDir, srcDir0, srcDir1, srcDir2]:
    srcPath = DIR + "/%s.day"%(ID)
    if os.path.exists(srcPath):
      break

  f=open(srcPath, "r")
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

  lout = deque([])
  lv   = deque([])
  for iline, line in enumerate(linesBody):
    line = line.split(";")
    DATE = line[0]
    Year = int(DATE[:4])
    Mon  = int(DATE[5:7])
    Day  = int(DATE[8:10])
    v    = float(line[3])
    print Year,Mon,Day,v

    if Mon != MonNow:
      if iline ==0:
        continue
      else:
        mv    = ma.masked_less(array(lv),0.0).sum() * coef
        if ma.is_masked(mv):
          mv = miss_out
        lout.append(["%04d-%02d"%(YearNow,MonNow),mv])
        print Year,Mon 
        lv      = deque([v])
        YearNow = Year
        MonNow  = Mon
    else:
      lv.append(v)
  #-- convert unit --------

  #coef  = 60*60*24./ dAra[Site] / 1.0e+3  # m3/s --> mm/m2
  #mv    = ma.masked_less(array(lv),0.0).sum() * coef  mm/m2/month

  coef  = 1.0  # m3/s 
  mv    = ma.masked_less(array(lv),0.0).mean() # m3/s

  #-- save ----------------
  lout.append(["%04d-%02d"%(Year,Mon),mv])

  print lout
  ocsv  = util.list2csv(lout)
  #oDir  = oBaseDir + "/%s"%(Site)
  oDir  = oBaseDir + "/Monthly"
  #oPath = oDir + "/Monthly.Obs.GRDC.%s.csv"%(Site)
  oPath = oDir + "/%s.csv"%(ID)
  util.mk_dir(oDir)
  f=open(oPath,"w"); f.write(ocsv); f.close()
  print oPath





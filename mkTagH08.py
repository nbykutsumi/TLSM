from numpy import *
from datetime import datetime, timedelta
from detect import TagRegrid, detect_func
#import Reanalysis
import calendar
import ConstH08
import sys
#import detect_func

iYM    = [1999,12]
eYM    = [2014,12]
#iYM    = [1990,1]
#eYM    = [1991,1]


model  = "JRA55"
ltag     = ["tc","c","fbc","ms"]
ltag_2nd = ["ms"]
ltag_all = ltag + ["ot"]
res    = "one"
endian = "little"
#*********************
if   res == "hlf":
  LatOut = arange(-89.75,89.75+0.01, 0.5)
  LonOut = arange(0.25, 359.75+0.01, 0.5)
elif res == "one":
  LatOut = arange(-89.5,89.5+0.01, 1.0)
  LonOut = arange(0.5, 359.5+0.01, 1.0)


ny, nx = len(LatOut), len(LonOut)

#** Functions ********
def saTOnp_3D(a): 
  return roll(a[:,::-1,:], shape(a)[2]/2, axis=2)

def ret_lYM(iYM, eYM):
  iYear, iMon = iYM
  eYear, eMon = eYM
  if iYear==eYear:
    lYM = [[iYear,Mon] for Mon in range(iMon,eMon+1)]
  else:
    lYM = [[iYear,Mon] for Mon in range(iMon,12+1)]

    lYM = lYM + [[Year,Mon] \
                  for Year in range(iYear+1,eYear)\
                  for Mon  in range(1,12+1)]

    lYM = lYM + [[eYear,Mon] for Mon in range(1,eMon+1)]
  return lYM

def ret_lDTime(iDTime,eDTime,dDTime):
  total_steps = int( (eDTime - iDTime).total_seconds() / dDTime.total_seconds() + 1 )
  return [iDTime + dDTime*i for i in range(total_steps)]

def mk_a3MaskDay(Year,Mon,Day, ltag, Lastday=False):
  if Lastday==False:
    lDTime = ret_lDTime(datetime(Year,Mon,Day,0), datetime(Year,Mon,Day,0)+timedelta(hours=24), timedelta(hours=6))
  else:
    lDTime = ret_lDTime(datetime(Year,Mon,Day,0), datetime(Year,Mon,Day,0)+timedelta(hours=18), timedelta(hours=6))
  
  l2out  = []
  lwgt   = []
  for DTime in lDTime:
    #------
    if DTime.hour ==0:
      wgt = 0.5
    else:
      wgt = 1.0
    lwgt.append(wgt)
    #------
    da2Mask = T.mkMaskFracRegrid(ltag=ltag, DTime=DTime, ltag_2nd=ltag_2nd)
    l2out.append( wgt * array([da2Mask[tag] for tag in ltag_all]).flatten())
  return (asarray(l2out).sum(axis=0)/sum(lwgt)).reshape(len(ltag_all),ny,nx)
 
def save_list2txt(a1in, soPath):
  sout = "\n".join(map(str,a1in))
  f=open(soPath, "w")
  f.write(sout)
  f.close()
  print soPath

#*********************

T   = TagRegrid.TagRegrid(model=model, LatOut=LatOut, LonOut=LonOut)
CH08= ConstH08.ConstH08()

#--- make dir -----------
soDir    = CH08.path_TagH08(datetime(1900,1,1,0), model=model, wnflag="nn", nclass=len(ltag_all), res=res)[0]
detect_func.mk_dir(soDir)
#--- save meta data -----

spathLat = soDir + "/lat.txt"
spathLon = soDir + "/lon.txt"
save_list2txt(LatOut, spathLat)
save_list2txt(LonOut, spathLon)

spathTAGS = soDir + "/TAGS.txt"
sout = "\n".join(map(str, ltag_all))
f=open(spathTAGS, "w"); f.write(sout); f.close()

spathREADME = soDir + "/README.txt"
sout = "%s_endian"%(endian)
f=open(spathREADME, "w"); f.write(sout); f.close()

#------------------------
lYM  = ret_lYM(iYM, eYM)
iYear, iMon = iYM
eYear, eMon = eYM
YearPre     = -9999.
for Year, Mon in lYM:
  #-- initialize --
  if Year != YearPre:
    YearPrev = Year
    if iYear == eYear:
      T.init_cyclone(iYM,eYM,tctype="bst")
    elif Year == iYear:
      T.init_cyclone(iYM,[iYear+1,1],tctype="bst")
    elif Year == eYear:
      T.init_cyclone([Year,1],[Year,12],tctype="bst")
    else:
      T.init_cyclone([Year,1],[Year+1,1],tctype="bst")
  #----------------  
  iDay = 1
  eDay = calendar.monthrange(Year,Mon)[1]
  for Day in range(iDay,eDay+1):
    #--------------
    DTime  = datetime(Year,Mon,Day,0)
    if (Year,Mon,Day) == (eYear,eMon,eDay):
      lastday = True
    else:
      lastday = False
    #--------------
    a3Mask = mk_a3MaskDay(Year,Mon,Day,ltag, lastday)
    soPath = CH08.path_TagH08(DTime, model=model, wnflag="nn", nclass=len(ltag_all), res=res, tstep="day")[1]
    if endian == "little":
      saTOnp_3D(a3Mask).astype(float32).tofile(soPath)
    elif endian == "big":
      saTOnp_3D(a3Mask).astype(float32).byteswap().tofile(soPath)

    else:
      print "check endian:",endian
      sys.exit()
    print soPath

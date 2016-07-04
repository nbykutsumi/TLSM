from numpy import *
from gtool import gtopen
from myfunc.myfunc_fsub import *
from myfunc.IO import GSMaP
from myfunc.IO import GPCP
from datetime import datetime, timedelta
import UtilTLSM
import os, sys

#iDTime = datetime(2001,1,1,0)
#iDTime = datetime(2000,1,1,0)
iDTime = datetime(2010,4,1,0)
eDTime = datetime(2010,12,31,0)
#eDTime = datetime(2010,1,5,0)
ny,nx  = 180,360
Suf    = "one"
endian = "little"
miss_gpcp = -9999.

prtype  = "GSMaP"
prj     = "std.v5"

#prtype  = "GPCP1DD"
#prj     = "1dd_v1.2"
baseDir = "/tank/utsumi/data/H08/%s.%s"%(prtype, prj)
DirSnow = baseDir + "/Snowf"
DirRain = baseDir + "/Rainf"
UtilTLSM.mk_dir(DirSnow)
UtilTLSM.mk_dir(DirRain)


#**** Functions ******************
def loadRainSnow(DTime):
  sDate = "%04d%02d%02d"%(DTime.year, DTime.month, DTime.day)
  baseDir  = "/tank/utsumi/data/H08/ELSE.JRA55.L1_01u"
  snowPath = baseDir + "/Snowf/Snowf_%s.one"%(sDate)
  rainPath = baseDir + "/Rainf/Rainf_%s.one"%(sDate)
  #-----------
  if   endian=="little":
    a2snow   = fromfile(snowPath,float32).reshape(ny,nx)
    a2rain   = fromfile(rainPath,float32).reshape(ny,nx)
  elif endian=="big":
    a2snow   = fromfile(snowPath,float32).reshape(ny,nx).byteswap()
    a2rain   = fromfile(rainPath,float32).reshape(ny,nx).byteswap()
  else:
    print "check endian:",endian
    sys.exit()
  return a2rain, a2snow


def mkSnowFrac(DTime):
  sDate = "%04d%02d%02d"%(DTime.year, DTime.month, DTime.day)
  baseDir  = "/tank/utsumi/data/H08/ELSE.JRA55.L1_01u"
  snowPath = baseDir + "/Snowf/Snowf_%s.one"%(sDate)
  rainPath = baseDir + "/Rainf/Rainf_%s.one"%(sDate)
  #-----------
  if   endian=="little":
    a2snow   = fromfile(snowPath,float32).reshape(ny,nx)
    a2rain   = fromfile(rainPath,float32).reshape(ny,nx)
  elif endian=="big":
    a2snow   = fromfile(snowPath,float32).reshape(ny,nx).byteswap()
    a2rain   = fromfile(rainPath,float32).reshape(ny,nx).byteswap()
  else:
    print "check endian:",endian
    sys.exit()
  #-----------
  a2prcp   = a2snow + a2rain
  return (ma.masked_where(a2prcp==0.0, a2snow)/a2prcp).filled(0.0)

def ret_oPath(prtype,DTime):
  sDate     = "%04d%02d%02d"%(DTime.year,DTime.month,DTime.day)
  PathRain  = DirRain + "/Rainf_%s.%s"%(sDate, Suf)
  PathSnow  = DirSnow + "/Snowf_%s.%s"%(sDate, Suf)
  return PathRain, PathSnow


#*********************************
def mkGSMaP(prj, iDTime, eDTime):
  if prj=="std.v5":
    gsmap  = GSMaP.GSMaP(prj="standard",ver="v5") 
    #--- prep for upscale -------
    a1lon_org      = gsmap.Lon
    a1lat_org      = gsmap.Lat
    a1lon_upscale  = arange(0.5,359.5+0.01,1.0)
    a1lat_upscale  = arange(-59.5,59.5+0.01, 1.0)
    miss_out       = 0.0
    lupscale_prep  = myfunc_fsub.upscale_prep( a1lon_org, a1lat_org, a1lon_upscale, a1lat_upscale, miss_out)
    a1xw_corres_fort  = lupscale_prep[0]
    a1xe_corres_fort  = lupscale_prep[1]
    a1ys_corres_fort  = lupscale_prep[2]
    a1yn_corres_fort  = lupscale_prep[3]
    a2areasw          = lupscale_prep[4].T
    a2arease          = lupscale_prep[5].T
    a2areanw          = lupscale_prep[6].T
    a2areane          = lupscale_prep[7].T

    #----------------------------

    lDTime = UtilTLSM.ret_lDTime(iDTime,eDTime,timedelta(days=1))
    for i,DTime in enumerate(lDTime):
      a2org = gsmap.time_ave_mmh(DTime, DTime+timedelta(hours=23),timedelta(hours=1)) / (60*60)

      #---- upscale --------
      pergrid           = 0
      missflag          = 0
      a2prcp            = myfunc_fsub.upscale_fast(a2org.T\
                        , a1xw_corres_fort, a1xe_corres_fort\
                        , a1ys_corres_fort, a1yn_corres_fort\
                        , a2areasw.T, a2arease.T, a2areanw.T, a2areane.T\
                        , len(a1lon_upscale), len(a1lat_upscale)\
                        , pergrid, missflag, miss_out\
                        ).T

      a2prcp = flipud(c_[a2prcp[:,180:], a2prcp[:,:180]])
      a2snowfrc = mkSnowFrac(DTime)[30:150]
      a2snow    = a2prcp*a2snowfrc
      a2rain    = a2prcp - a2snow

      #----- fill hight latitudes ---
      a2rain_glb, a2snow_glb = loadRainSnow(DTime)
      a2rain_glb[30:150] = a2rain
      a2snow_glb[30:150] = a2snow
      #---------
      PathRain, PathSnow = ret_oPath(prtype,DTime)
      #-----------
      if   endian=="little": 
        a2snow_glb.astype(float32).tofile(PathSnow)
        a2rain_glb.astype(float32).tofile(PathRain)
      elif endian=="big":
        a2snow_glb.astype(float32).byteswap().tofile(PathSnow)
        a2rain_glb.astype(float32).byteswap().tofile(PathRain)
      else:
        sys.exit()
      #-----------
      print PathSnow




def mkGPCP(prj, iDTime, eDTime):
  dDTime = timedelta(days=1)
  lDTime = UtilTLSM.ret_lDTime(iDTime,eDTime,dDTime)
  gpcp   = GPCP.GPCP(prj=prj)
  gpcp(iDTime,eDTime)
  a3dat  = gpcp.Data
  a3dat  = ma.masked_equal(a3dat, miss_gpcp).filled(0.0)
  
  for i,DTime in enumerate(lDTime):
    a2snowfrc = mkSnowFrac(DTime)
    a2prcp    = flipud(c_[a3dat[i,:,180:], a3dat[i,:,:180]])
    a2snow    = a2prcp*a2snowfrc
    a2rain    = a2prcp - a2snow
    PathRain, PathSnow = ret_oPath(prtype,DTime)
  
    #-----------
    if   endian=="little": 
      a2snow.astype(float32).tofile(PathSnow)
      a2rain.astype(float32).tofile(PathRain)
    elif endian=="big":
      a2snow.astype(float32).byteswap().tofile(PathSnow)
      a2rain.astype(float32).byteswap().tofile(PathRain)
    else:
      sys.exit()
    #-----------
    print PathSnow

#**** main ******************
if   prtype=="GPCP1DD":
  mkGPCP(prj, iDTime, eDTime)

elif prtype=="GSMaP":
  mkGSMaP(prj, iDTime, eDTime)

else:
  print "check prtype",prtype
  sys.exit()

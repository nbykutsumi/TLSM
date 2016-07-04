from numpy import *
from datetime import datetime, timedelta
import myfunc.util as util
import ConstH08
import os, sys
import calendar
import H08

iYM  = [1990,1]
eYM  = [2010,12]
lYM  = util.ret_lYM(iYM, eYM)

PRJ = "JR55"
RUN = "____"

ntag   = 5
# see "/tank/utsumi/tag.mask/JRA55.nn.04c.one/TAGS.txt"
H08Dir  = "/tank/utsumi/H08/H08_20130501"
res     = "one"
ny,nx   = 180,360

h08     = H08.H08(prj=PRJ, run=RUN, res=res)
CH08    = ConstH08.ConstH08()
dPrcpDir  = {"JR55": "/tank/utsumi/data/H08/ELSE.JRA55.L1_01u"}

#******************************
def load_Prcp(DTime, PRJ):
  RainfDir  = dPrcpDir[PRJ] + "/Rainf"
  SnowfDir  = dPrcpDir[PRJ] + "/Snowf"
  stime     = "%04d%02d%02d"%(DTime.year, DTime.month, DTime.day)
  RainfPath = RainfDir + "/Rainf_%s.one"%(stime)
  SnowfPath = SnowfDir + "/Snowf_%s.one"%(stime)
  a2Rainf   = fromfile(RainfPath, float32).reshape(ny,nx)
  a2Snowf   = fromfile(SnowfPath, float32).reshape(ny,nx)
  return  a2Rainf + a2Snowf
#******************************
def ret_ltag(ntag):
  srcPath = "/tank/utsumi/tag.mask/JRA55.nn.%02dc.one/TAGS.txt"%(ntag)
  f=open(srcPath, "r")
  lines = f.readlines()
  f.close()
  return [s.strip() for s in lines]

#******************************

ltag   = ret_ltag(ntag)
for Year,Mon in lYM:
  eDay   = calendar.monthrange(Year,Mon)[1]
  iDTime = datetime(Year,Mon,1,0)
  eDTime = datetime(Year,Mon,eDay,23)
  dDTime = timedelta(hours=24)
  lDTime = util.ret_lDTime(iDTime, eDTime, dDTime)

  a3tagprcp = zeros([ntag, ny, nx], float32)
  for DTime in lDTime:
    print DTime
    a2prcp  = load_Prcp(DTime, PRJ)

    frcPath = CH08.path_TagH08(DTime, model="JRA55", wnflag="nn", nclass=ntag, res="one", tstep="day")[1]
    a3frc   = fromfile(frcPath, float32).reshape(ntag, ny, nx)
    for i in range(ntag):
      a3tagprcp[i] = a3tagprcp[i] + a2prcp * a3frc[i] 

  a3tagprcp = a3tagprcp / len(lDTime)   # average
  #-- save -----
  rootDir, srcDir, srcPath = h08.ret_pathTagVarMon(var="PRCP", ntag=ntag, Year=Year, Mon=Mon) 

  util.mk_dir(srcDir)
  a3tagprcp.tofile(srcPath)
  print srcPath 


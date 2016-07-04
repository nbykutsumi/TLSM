from numpy import *
from datetime import datetime, timedelta
import myfunc.util as util
import os, sys
import calendar
import H08

iYM    = [1990,1]
#eYM    = [1990,1]
eYM    = [2010,12]
lYM    = util.ret_lYM(iYM,eYM)
#PRJ="JR55"
#PRJ="GPCP"
#PRJ="GSMP"
#lPRJ = ["JR55","GPCP","GSMP"]
PRJ = "JR55"
RUN="____"

#var    = "riv_out_"
#var    = "Qtot____"
#var    = "Evap____"
#var    = "SoilMois"

lvar   = ["riv_out_","Qtot____","Evap____","SoilMois"]

ntag   = 5
H08Dir  = "/tank/utsumi/H08/H08_20130501"
orivDir ="%s/riv/out"%(H08Dir)
olndDir ="%s/lnd/out"%(H08Dir)
ptagDir ="/tank/utsumi/tag.mask/JRA55.nn.%04dc.one"%(ntag)
res= "one"
ny,nx = 180,360

H08   = H08.H08(prj=PRJ, run=RUN, res=res)
#----------------------
def load_a2dat(var,DTime):
  Year,Mon,Day = DTime.year, DTime.month, DTime.day
  if var in ["Evap____","SubSnow_","Qtot____","SoilMois","SWE_____"]:
    sPath = olndDir + "/%s"%(var) + "/%s%s%04d%02d%02d.%s"%(PRJ,RUN,Year,Mon,Day,res)

  elif var in ["Rainf___"]:
    sPath = ilndDir + "/Rainf" + "/Rainf_%04d%02d%02d.%s"%(Year,Mon,Day,res)

  elif var in ["Snowf___"]:
    sPath = ilndDir + "/Snowf" + "/Snowf_%04d%02d%02d.%s"%(Year,Mon,Day,res)

  elif var in ["riv_out_","riv_sto_"]:
    sPath = orivDir + "/%s"%(var) + "/%s%s%04d%02d%02d.%s"%(PRJ,RUN,Year,Mon,Day,res)

  return fromfile(sPath, float32).reshape(ny,nx)
#----------------------
def load_a3tag(var,DTime):
  Year,Mon,Day = DTime.year, DTime.month, DTime.day
  if var in ["FrcSWE__","FrcSoilM"]:
    sPath = olndDir + "/%s"%(var) + "/%s%s%04d%02d%02d.%s"%(PRJ,RUN,Year,Mon,Day,res)
  elif var in ["FrcPrcp"]:
    sPath = ptagDir + "/tag_%04d%02d%02d.%s"%(Year,Mon,Day,res)
  elif var in ["Frc_sto_"]:
    sPath = orivDir + "/%s"%(var) + "/%s%s%04d%02d%02d.%s"%(PRJ,RUN,Year,Mon,Day,res)
  return fromfile(sPath, float32).reshape(ntag,ny,nx)
#----------------------
for var in lvar:
  for Year,Mon in lYM:
    eDay   = calendar.monthrange(Year,Mon)[1]
    iDTime = datetime(Year,Mon,1,0)
    eDTime = datetime(Year,Mon,eDay,0)
    lDTime = util.ret_lDTime(iDTime, eDTime,timedelta(days=1))
  
    #- initialize -------
    a3tagdat  = zeros([ntag,ny,nx],float32)
  
    #--------------------
    for i,DTime in enumerate(lDTime):
      print DTime
      if var   in ["riv_out_"]:
        a3frc = load_a3tag("Frc_sto_",DTime)
      elif var in ["Qtot____","SoilMois","Evap____","SoilMois"]:
        a3frc = load_a3tag("FrcSoilM", DTime)
  
      a2dat = load_a2dat(var, DTime)
  
      for i in range(ntag):
        a3tagdat[i] = a3tagdat[i] + a3frc[i]*a2dat
  
    a3tagdat = a3tagdat / len(lDTime)   # average
    #--- save ------------
  
    rootDir, oDir, oPath = H08.ret_pathTagVarMon(var, ntag, Year, Mon)
    util.mk_dir(oDir)
  
    a3tagdat.tofile(oPath)
    print oPath
  

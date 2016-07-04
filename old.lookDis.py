from numpy import *
import myfunc.util as util
from datetime import datetime, timedelta
import os, sys
import calendar

iYM    = [2001,1]
#eYM    = [1990,1]
eYM    = [2009,12]
lYM    = util.ret_lYM(iYM,eYM)
#PRJ="JR55"
#PRJ="GPCP"
#PRJ="GSMP"
#lPRJ = ["JR55","GPCP","GSMP"]
lPRJ = ["JR55"]
RUN="____"
#lSite = ["Datong","Bahadurabad","Vicksburg","StungTreng","Obidos"]
lSite = ["Obidos"]
dyx   = {
         "Datong"    :[60,296]
        ,"Bahadurabad":[65,269] 
        ,"Vicksburg":[56,88 ]
        ,"StungTreng":[76,285]
        ,"Obidos"   :[92,124]
        }


#dyx   = {"Obidos"   :[92,124]
#        ,"Thebes"   :[52,90 ]
#        ,"Vicksburg":[56,88 ]
#        }

#ltag   = ["tc","c","fbc","ms","ot"]
ltag   = ["tc","c","fbc","ot"]
# see "/tank/utsumi/tag.mask/JRA55.nn.04c.one/TAGS.txt"
ntag   = len(ltag)
H08Dir  = "/tank/utsumi/H08/H08_20130501"
orivDir ="%s/riv/out"%(H08Dir)
ptagDir ="/tank/utsumi/tag.mask/JRA55.nn.%04dc.one"%(ntag)
res= "one"
ny,nx = 180,360

#flwdirPath = H08Dir + "/map/dat/flw_dir_/flwdir.GSWP2.one"
#rivnumPath = H08Dir + "/map/out/riv_num_/rivnum.GSWP2.one"
rivaraPath = H08Dir + "/map/out/riv_ara_/rivara.GSWP2.one"

#a2flwdir = fromfile(flwdirPath, float32).reshape(ny,nx)
#a2rivnum = fromfile(rivnumPath, float32).reshape(ny,nx)
a2rivara = fromfile(rivaraPath, float32).reshape(ny,nx)
#print a2flwdir
#print a2rivnum

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

X,Y     = meshgrid(arange(0,nx,1.0),arange(0,ny,1.0))

dAra = {}
for Site in lSite:
  y,x        = dyx[Site]
  dAra[Site] = a2rivara[y,x]

for PRJ in lPRJ:
  for Year,Mon in lYM:
    eDay   = calendar.monthrange(Year,Mon)[1]
    iDTime = datetime(Year,Mon,1,0)
    eDTime = datetime(Year,Mon,eDay,0)
    lDTime = util.ret_lDTime(iDTime, eDTime,timedelta(days=1))
  
    #- initialize -------
    dv  = {}
    for Site in lSite:
      for tag in ltag+["tot"]:
        dv[Site, tag] = []
    #--------------------
    for i,DTime in enumerate(lDTime):
      print DTime
      a2rivout = load_a2dat("riv_out_", DTime)
      a3frcsto = load_a3tag("Frc_sto_",DTime)
      for Site in lSite:
        y,x = dyx[Site]
        dv[Site,"tot"].append( a2rivout[y,x] )
      for itag, tag in enumerate(ltag):
        y,x      = dyx[Site]
        a2tagout = a3frcsto[itag]*a2rivout
        for Site in lSite:
          y,x = dyx[Site]
          dv[Site, tag].append( a2tagout[y,x] )
  
    #- output ----------
    for Site in lSite:
      a2out = empty([eDay,len(ltag)+1])
      for itag, tag in enumerate(["tot"]+ltag):
        a1v = array(dv[Site,tag])*60*60*24./dAra[Site]
        a2out[:,itag] = a1v
  
      sout = util.array2csv(a2out)
      #- save ----------
      obaseDir = "/tank/utsumi/H08/out/TAGFLW/%02dc"%(ntag)
      oDir     = obaseDir + "/%s"%(Site)
      util.mk_dir(oDir)
      oPath    = oDir + "/%s%s%04d%02d.csv"%(PRJ,RUN,Year,Mon)
      f=open(oPath,"w"); f.write(sout); f.close()
      print oPath

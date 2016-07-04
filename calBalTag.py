from numpy import *
from datetime import datetime, timedelta
import UtilTLSM
import sys

lndflg  = True
rivflg  = False
iDTime  = datetime(2001,1,2,0)
#eDTime  = datetime(1990,12,31,0)
eDTime  = datetime(2001,12,30,0)
#eDTime  = datetime(1990,1,2,0)
dDTime  = timedelta(days=1)
#PRJ="JR55"
#PRJ="GPCP"
PRJ="GSMP"
RUN="____"

#H08Dir  = "/data3/utsumi/H08/H08_20130501"
H08Dir  = "/tank/utsumi/H08/H08_20130501"
olndDir ="%s/lnd/out"%(H08Dir)
if   PRJ=="GSW2":
  ilndDir ="/export/nas29/nas29/yano/GSWP2_one/met/dat"
elif PRJ=="JR55":
  ilndDir ="/tank/utsumi/data/H08/ELSE.JRA55.L1_01u"
elif PRJ=="GPCP":
  ilndDir ="/tank/utsumi/data/H08/GPCP1DD.1dd_v1.2"
elif PRJ=="GSMP":
  ilndDir ="/tank/utsumi/data/H08/GSMaP.std.v5"
else:
  print "check PRJ:",PRJ
  sys.exit()

orivDir ="%s/riv/out"%(H08Dir)
ptagDir ="/tank/utsumi/tag.mask/JRA55.nn.04c.one"
res= "one"
ny,nx = 180,360
ntag  = 4
miss  = 1.e+20

#----------------------
#lndara_path= "/data3/utsumi/H08/H08_20130501/map/dat/lnd_ara_/lndara.GSWP2.one"
lndara_path= "%s/map/dat/lnd_ara_/lndara.GSWP2.one"%(H08Dir)
a2lndara  = fromfile(lndara_path,float32).reshape(ny,nx)
a2lndara  = ma.masked_greater(a2lndara, 1.0e+19).filled(0.0)

#flwdir_path= "/data3/utsumi/H08/H08_20130501/map/dat/flw_dir_/flwdir.GSWP2.one"
flwdir_path= "%s/map/dat/flw_dir_/flwdir.GSWP2.one"%(H08Dir)
a2flwdir  = fromfile(flwdir_path, float32).reshape(ny,nx)
a3flwdir  = array([a2flwdir for i in range(ntag)])

rivnum_path = "%s/map/out/riv_num_/rivnum.GSWP2.one"%(H08Dir)
a2rivnum    = fromfile(rivnum_path, float32).reshape(ny,nx)
a3rivnum    = array([a2rivnum for i in range(ntag)])
#----------------------
def load_a2dat(var,DTime):
  Year,Mon,Day = DTime.year, DTime.month, DTime.day
  if var in ["Evap____","SubSnow_","Qtot____","SoilMois","SWE_____"]:
    sPath = olndDir + "/%s"%(var) + "/%s%s%04d%02d%02d.%s"%(PRJ,RUN,Year,Mon,Day,res)
  elif var in ["Rainf___"]:
    #sPath = ilndDir + "/%s"%(var) + "/GSW2B1b_%04d%02d%02d.%s"%(Year,Mon,Day,res)
    sPath = ilndDir + "/Rainf" + "/Rainf_%04d%02d%02d.%s"%(Year,Mon,Day,res)
  elif var in ["Snowf___"]:
    #sPath = ilndDir + "/%s"%(var) + "/GSW2B1b_%04d%02d%02d.%s"%(Year,Mon,Day,res)
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

#**************************************************
#  watar balance of Land
#--------------------------------------------------
if lndflg == True:
  lDTime = UtilTLSM.ret_lDTime(iDTime, eDTime, dDTime)
  a3Rainf    = zeros([ntag,ny,nx],float32)
  a3Snowf    = zeros([ntag,ny,nx],float32)
  a3ET       = zeros([ntag,ny,nx],float32)
  a3SubSnow  = zeros([ntag,ny,nx],float32)
  a3Qtot     = zeros([ntag,ny,nx],float32)
  for DTime in lDTime:
    print DTime
    a3FrcPrcp  = load_a3tag("FrcPrcp" ,DTime)
    a3FrcSoilM = load_a3tag("FrcSoilM",DTime)
    a3FrcSWE   = load_a3tag("FrcSWE__"  ,DTime)
    a3Rainf    = a3Rainf   + load_a2dat("Rainf___",DTime)*a3FrcPrcp
    a3Snowf    = a3Snowf   + load_a2dat("Snowf___",DTime)*a3FrcPrcp
    a3Qtot     = a3Qtot    + load_a2dat("Qtot____",DTime)*a3FrcSoilM
  
    a2Evap_tmp    = load_a2dat("Evap____",DTime)
    a2SubSnow_tmp = load_a2dat("SubSnow_",DTime)
    a3ET       = a3ET      + (a2Evap_tmp-a2SubSnow_tmp)  *a3FrcSoilM
    a3SubSnow  = a3SubSnow + a2SubSnow_tmp *a3FrcSWE
  
  a3Rainf  = a3Rainf  *dDTime.total_seconds()*a2lndara
  a3Snowf  = a3Snowf  *dDTime.total_seconds()*a2lndara
  a3Qtot   = a3Qtot   *dDTime.total_seconds()*a2lndara
  a3ET     = a3ET     *dDTime.total_seconds()*a2lndara
  a3SubSnow= a3SubSnow*dDTime.total_seconds()*a2lndara
  
  
  a3SoilM_ini= ( ma.masked_greater(load_a2dat("SoilMois",iDTime-dDTime),1e+19)\
               *ma.masked_greater(load_a3tag("FrcSoilM",iDTime-dDTime),1e+19)).filled(0.0)
  a3SWE_ini  = ( ma.masked_greater(load_a2dat("SWE_____",iDTime-dDTime),1e+19)\
               *ma.masked_greater(load_a3tag("FrcSWE__",iDTime-dDTime),1e+19)).filled(0.0)
  
  a3SoilM_end= load_a2dat("SoilMois",eDTime)        * load_a3tag("FrcSoilM",eDTime)
  a3SWE_end  = load_a2dat("SWE_____",eDTime)        * load_a3tag("FrcSWE__",eDTime)
  
  a3SoilM_ini = a3SoilM_ini * a2lndara
  a3SoilM_end = a3SoilM_end * a2lndara
  a3SWE_ini   = a3SWE_ini   * a2lndara
  a3SWE_end   = a3SWE_end   * a2lndara
  
  
  print "iDTime=",iDTime
  print "eDTime=",eDTime
  for i in range(ntag):
  #for i in [2]:
    print "*** water balance of Land [km3/period] ****"
    Rainf   = a3Rainf[i]
    Snowf   = a3Snowf[i]
    ET      = a3ET[i]
    SubSnow = a3SubSnow[i]
    Qtot    = a3Qtot[i]
    dSoilM  = (a3SoilM_end - a3SoilM_ini)[i]
    dSWE    = (a3SWE_end   - a3SWE_ini  )[i]
    Bal     = Rainf+Snowf-ET-SubSnow-Qtot-dSoilM-dSWE
    print "itag=    ", i
    print "+Rainf   ", "%.4e"%(Rainf.sum()    /1.e+12)
    print "+Snowf   ", "%.4e"%(Snowf.sum()    /1.e+12)
    print "-ET      ", "%.4e"%-(ET.sum()      /1.e+12)
    print "-SubSnow ", "%.4e"%-(SubSnow.sum() /1.e+12)
    print "-Qtot    ", "%.4e"%-(Qtot.sum()    /1.e+12)
    print "-dSoilM  ", "%.4e"%-(dSoilM.sum()  /1.e+12)
    print "-dSWE    ", "%.4e"%-(dSWE.sum()    /1.e+12)
    print "=Bal[km3]", "%.4e"%(Bal.sum()      /1.e+12)  # kg --> km^3

#**************************************************
#  watar balance of River
#--------------------------------------------------
iy, ix = 6, 143
i0l    = nx*(iy+1-1)+(ix+1)
print "i0l=",i0l
if rivflg == True:
  lDTime = UtilTLSM.ret_lDTime(iDTime, eDTime, dDTime)
  a3Qtot   = zeros([ntag,ny,nx],float32)
  a3Rivout = zeros([ntag,ny,nx],float32)

  for DTime in lDTime:
    a3FrcSoilM = load_a3tag("FrcSoilM",DTime)
    a3FrcSto   = load_a3tag("Frc_sto_",DTime)
    a3Qtot     = a3Qtot   + load_a2dat("Qtot____",DTime)*a3FrcSoilM
    a3Rivout   = a3Rivout + load_a2dat("riv_out_",DTime)*a3FrcSto

  a3Qtot   = a3Qtot \
             * ma.masked_greater(a2lndara,1.e+19).filled(0.0)\
             *dDTime.total_seconds()

  a3Rivout = ma.masked_where(a3flwdir !=9, a3Rivout).filled(0.0) \
                         * dDTime.total_seconds()
  
  a3Sto_ini =load_a2dat("riv_sto_",iDTime-dDTime)\
             *load_a3tag("Frc_sto_",iDTime-dDTime)\
  
  a3Sto_end =load_a2dat("riv_sto_",eDTime)\
             *load_a3tag("Frc_sto_",eDTime)
  #--- Mask ------------------
  a3Qtot    = ma.masked_where(a3rivnum==0, a3Qtot   )
  a3Rivout  = ma.masked_where(a3rivnum==0, a3Rivout )
  a3Sto_ini = ma.masked_where(a3rivnum==0, a3Sto_ini)
  a3Sto_end = ma.masked_where(a3rivnum==0, a3Sto_end)
  print "iDTime=",iDTime
  print "eDTime=",eDTime
  for i in range(ntag):
    print "*** water balance of River [km3/period] ****"
    Qtot   = a3Qtot[i]
    Rivout = a3Rivout[i]
    dSto   = (a3Sto_end - a3Sto_ini)[i]
    Bal    = Qtot - Rivout - dSto
    print "itag=    ", i
    print "+Qtot    ", "%.4e"%(Qtot  .sum()   /1.e+12)
    print "-Rivout  ", "%.4e"%(-Rivout.sum()  /1.e+12)
    print "-dSto    ", "%.4e"%(-dSto.sum()    /1.e+12)
    print "=Bal[km3]", "%.4e"%(Bal.sum()      /1.e+12) # kg--> km^3
 

from numpy import *
from datetime import datetime, timedelta
import calendar
import ConstH08
import H08
import UtilTLSM
import myfunc.util as util

model= "JRA55"
PRJ  = "JR55"
RUN  = "____"
crd  = "np"
res  = "one"

iYM  = [2000,1]
eYM  = [2000,12]
lYM  = util.ret_lYM(iYM,eYM)

ny,nx = 180,360
ntag  = 5

h08 = H08.H08(prj=PRJ, run=RUN, res=res)
dPrcpDir  = {"JR55": "/tank/utsumi/data/H08/ELSE.JRA55.L1_01u"}

#****************************

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
#****************************

iYear,iMon = iYM
eYear,eMon = eYM
iDTime = datetime(iYear,iMon,1,0)
eDTime = datetime(eYear,eMon,calendar.monthrange(eYear,eMon)[1],0)
dDTime = timedelta(hours=24)
print iDTime, eDTime
lDTime = UtilTLSM.ret_lDTime(iDTime, eDTime, dDTime)
#-- vars -----------
lvar     = ["Evap____"]
#lvar     = ["Qtot____"]
#lvar     = ["riv_out_"]
#lvar     = ["SoilMois"]

da2var0  = {}
for var in lvar:
  #-----------------
  a2var0 = zeros([ny,nx])
  for DTime in lDTime:
    a2var0 = a2var0 + h08.load_H08var(var,DTime)
  a2var0 = a2var0 / len(lDTime)

  #
  a3tagvar   = zeros([ntag,ny,nx],float32)
  for YM in lYM:  
    Year,Mon = YM
    a3tagvar = a3tagvar + h08.loadTagVarMon(var,ntag,Year,Mon)
  a3tagvar = a3tagvar/len(lYM)
  a2var1   = a3tagvar.sum(axis=0)

  a2dvar   = a2var1 - a2var0
  a2bias   = ma.masked_where(a2var0==0.0, a2dvar)/a2var0
  print a2var0.sum(), a2var1.sum()

  a3frac   = empty([ntag,ny,nx])
  for itag in range(ntag):
    a3frac[itag] = (ma.masked_where(a2var1==0.0, a3tagvar[itag])/a2var1).filled(0.0)

#-- prcp -----------
a2prcp0 = zeros([ny,nx],float32)
for DTime in lDTime:
  a2prcp0 = a2prcp0 + load_Prcp(DTime, PRJ)
a2prcp0 = a2prcp0 / len(lDTime)

a3tagprcp = zeros([ntag,ny,nx],float32)
for YM in lYM:
  Year,Mon = YM
  a3tagprcp= a3tagprcp + h08.loadTagVarMon("PRCP",ntag,Year,Mon)
a3tagprcp = a3tagprcp/len(lYM)
a2prcp1   = a3tagprcp.sum(axis=0)

a3frcprcp = empty([ntag,ny,nx])
for itag in range(ntag):
  a3frcprcp[itag] = (ma.masked_where(a2prcp1==0.0, a3tagprcp[itag])/a2prcp1).filled(0.0)


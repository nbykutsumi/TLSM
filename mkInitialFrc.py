from numpy import *
from datetime import datetime, timedelta
import ConstH08
import UtilTLSM

iDTime = datetime(1990,1,1,0)
eDTime = datetime(1990,12,31,0)
#eDTime = datetime(1990,1,3,0)
dDTime = timedelta(hours=24)
lDTime = UtilTLSM.ret_lDTime(iDTime, eDTime, dDTime)

res    = "one"
nclass = 5

if res=="one":
  ny,nx = 180,360


CH08 = ConstH08.ConstH08()
#----- Initial value for FrcSoilM ----
a3out  = zeros([nclass, ny,nx],float32)
for DTime in lDTime:
  tagPath = CH08.path_TagH08(DTime, model="JRA55",wnflag="nn", nclass=nclass, res=res, tstep="day")[1]
  #a3out   = a3out + fromfile(tagPath, float32).reshape(nclass,ny,nx).byteswap()
  a3out   = a3out + fromfile(tagPath, float32).reshape(nclass,ny,nx)
  print DTime
a3out = a3out/len(lDTime)

oDir  = CH08.path_TagH08(iDTime, model="JRA55",wnflag="nn", nclass=nclass, res=res, tstep="day")[0]
oPath = oDir + "/" + "tag_%04d_%04d.%s"%(iDTime.year, eDTime.year, res)
#a3out.byteswap().tofile(oPath)
a3out.tofile(oPath)
print oPath


#----- Initial value for FrcSWE ----
a3frcswe = zeros([nclass, ny,nx],float32)
for DTime in lDTime:
  Year  = DTime.year
  Mon   = DTime.month
  Day   = DTime.day
  tagPath = CH08.path_TagH08(DTime, model="JRA55",wnflag="nn", nclass=nclass, res=res, tstep="day")[1]
  #a3tag   = a3frcswe + fromfile(tagPath, float32).reshape(nclass,ny,nx).byteswap()
  a3tag   = a3frcswe + fromfile(tagPath, float32).reshape(nclass,ny,nx)

  snowPath= "/export/nas29/nas29/yano/GSWP2_one/met/dat/Snowf___/GSW2B1b_%04d%02d%02d.one"%(Year,Mon,Day)
  #a2snow  = fromfile(snowPath, float32).reshape(ny,nx).byteswap()
  a2snow  = fromfile(snowPath, float32).reshape(ny,nx)

  a3frcswe = a3frcswe + multiply(a3tag, a2snow)

  print DTime
a3frcswe = ( ma.masked_where(a3frcswe.sum(axis=0)*ones([nclass,ny,nx]) ==0.0, a3frcswe)\
            /a3frcswe.sum(axis=0)\
           ).filled(1.0/nclass)

oDir  = CH08.path_TagH08(iDTime, model="JRA55",wnflag="nn", nclass=nclass, res=res, tstep="day")[0]
oPath = oDir + "/" + "InitFrcSWE_%04d_%04d.%s"%(iDTime.year, eDTime.year, res)
#a3frcswe.byteswap().tofile(oPath)
a3frcswe.tofile(oPath)
print oPath




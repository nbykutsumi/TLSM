from numpy import *
from gtool import gtopen
from myfunc.IO import GPCP
from datetime import datetime, timedelta
import sys
import UtilTLSM

iYear   = 1990
eYear   = 1998
#var     = "Snowf"
#var     = "Rainf"
#var     = "Tair"
lvar    = ["Rainf","Snowf","Tair","Wind","Qair","PSurf","LWdown","SWdown"]
#lvar    = ["PSurf"]
endian  = "little"

Suf     = "one"
ny,nx   = 180,360
def ret_coef(var):
  if var in ["PSurf"]:
    return 100.0
  else:
    return 1.0

for Year in range(iYear,eYear+1):
  for var in lvar:
    ibaseDir = "/data1/hjkim/ELSE/JRA55/in/L1_01u"
    iDir     = ibaseDir + "/%s"%(var)
    iPath    = iDir + "/%s_%04d.gt"%(var,Year)
    obaseDir = "/tank/utsumi/data/H08/ELSE.JRA55.L1_01u"
    oDir     = obaseDir + "/%s"%(var)
    UtilTLSM.mk_dir(oDir)
    coef     = ret_coef(var)

    gt = gtopen(iPath)
    a2dat = zeros([ny,nx],float32)
    for i,chunk in enumerate(gt):
      DATE = chunk.header["DATE"]
      DTime= datetime(int(DATE[:4]), int(DATE[4:6]), int(DATE[6:8]),int(DATE[9:11]))
      a2dat = a2dat + chunk.data[0]
      if DTime.hour ==21:
        a2dat = flipud(c_[a2dat[:,180:], a2dat[:,:180]])/8.0 * coef
        oPath = oDir + "/%s_%04d%02d%02d.%s"%(var,DTime.year,DTime.month,DTime.day,Suf)
        #---------------- 
        if endian=="little":
          a2dat.tofile(oPath)
        elif endian=="big":
          a2dat.byteswap().tofile(oPath)
        else:
          print "check endian:",endian
          sys.exit()
        #---------------- 
        a2dat = zeros([ny,nx],float32)
        print oPath

#gpcp = GPCP.GPCP("1dd_v1.2")
#gpcp(datetime(2000,1,1,0),datetime(2000,1,1,0))
#a2gpcp = gpcp.Data
#print a2gpcp
#
#aPath = "/export/nas29/nas29/yano/GSWP2_one/met/dat/Rainf___/GSW2B1b_19900101.one"
#a     = fromfile(aPath, float32).reshape(180,360).byteswap()

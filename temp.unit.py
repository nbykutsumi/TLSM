from gtool import gtopen
from numpy import *

Year    = 1990
Mon     = 1
Day     = 1
sDATE   = "%04d%02d%02d"%(Year,Mon,Day)
#lvar    = ["Rainf","Snowf","Tair","Wind","Qair","PSurf","LWdown","SWdown"]
lvar    = ["PSurf"]
dvar = {"Wind":"Wind____"\
       ,"Rainf":"Rainf___"\
       ,"Snowf":"Snowf___"\
       ,"Tair":"Tair____"\
       ,"Qair":"Qair____"\
       ,"PSurf":"PSurf___"\
       ,"SWdown":"SWdown__"\
       ,"LWdown":"LWdown__"}
a = {}
b = {}
for var in lvar:
  aPath = "/export/nas29/nas29/yano/GSWP2_one/met/dat/%s/GSW2B1b_%s.one"%(dvar[var],sDATE)
  bPath = "/tank/utsumi/data/H08/ELSE.JRA55.L1_01u/%s/%s_%s.one"%(var,var,sDATE)
  a[var]     = fromfile(aPath, float32).reshape(180,360).byteswap()
  b[var]     = fromfile(bPath, float32).reshape(180,360).byteswap()


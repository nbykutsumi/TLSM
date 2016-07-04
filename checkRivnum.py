from numpy import *

ny,nx = 180,360

lriv = ["Amazon","Mississippi","Yangtze","Brahmaputra","Mekong"]
dyx   = {
         "Amazon"      :[92,124]
        ,"Mississippi"   :[56,88 ]
        ,"Yangtze"      :[60,296]
        ,"Brahmaputra" :[65,269]
        ,"Mekong"  :[76,285]
        }

numPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_num_/rivnum.GSWP2.one"
a2num   = fromfile(numPath, float32).reshape(ny,nx)

for riv in lriv:
  iy,ix   = dyx[riv]
  rivnum  = a2num[iy,ix]
  print riv, rivnum

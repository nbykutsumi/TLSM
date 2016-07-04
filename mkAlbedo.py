from numpy import *
import os, sys

iYear = 1980
eYear = 2015
lYear = range(iYear,eYear+1)
lMon  = range(1,12+1)
#endian = "little"
endian = "big"

sDir = "/tank/utsumi/data/H08/Albedo/GSW2_%s"%(endian)

for Year in lYear:
  for Mon in lMon:
    srcPath = sDir + "/GSW2____1995%02d00.one"%(Mon)
    dstPath = sDir + "/Const___%04d%02d00.one"%(Year,Mon)
    if os.path.exists(srcPath):
      if os.path.islink(dstPath):
        os.unlink(dstPath)
     
      os.symlink(srcPath, dstPath)
      print dstPath
    else:
      print "nofile:", srcPath
      sys.exit()

from numpy import *
import GRDC

crd    = "np"
res    = "one"

listDir = "/tank/utsumi/data/TLSM/GRDC_Station"
iPath   = listDir + "/TargetStations.np.one.Aft1993.100000km2.filtered.2.csv"
oPath   = iPath[:-6] + ".3.csv"

f = open(iPath, "r")
lines = f.readlines()
f.close()

slabel  = lines[0]
dsline  = {}
dArea   = {}
for sline in lines[1:]:
  line   = sline.split(",")
  rivnum = int(line[1])
  Area   = float(line[11])

  if dArea.has_key(rivnum):
    if dArea[rivnum] < Area:
      dArea[rivnum] = Area
      dsline[rivnum] = sline
    else:
      continue
  else:
    dArea[rivnum] = Area
    dsline[rivnum] = sline

sout  = slabel

lrivnum = sort(dArea.keys())
for rivnum in lrivnum:
  sout  = sout + dsline[rivnum]

#--- write -----
f = open(oPath,"w")
f.write(sout)
f.close()
print oPath
  


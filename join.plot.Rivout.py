import Image
from numpy import *
import myfunc.IO.GRDC as GRDC

PRJ  = "JR55"
RUN  = "____"
ntag = 5
crd  = "np"
res  = "one"
var  = "riv_out_"

#*** Figure para *********
iyfig  = 1  # top
eyfig  = -1  # bottom
ixfig  = 20
exfig  = -5

thnrmse= 0.5

#-- load Target Station List -------
listDir = "/tank/utsumi/data/TLSM/GRDC_Station"
#TargetListName  = listDir + "/Target.over10yr100000km2.csv"
TargetListName  = listDir + "/TargetStations.np.one.Aft1993.100000km2.filtered.3.csv"
f=open(TargetListName, "r")
lines = f.readlines()
f.close()
ltarget   = []
lstnID    = []
for sline in lines[1:]:
  line           = sline.strip().split(",")
  nrmse          = float(line[0])
  if (nrmse >thnrmse)or(nrmse<0):
    continue

  rivnum         = int(line[1])
  yx             = [float(line[2]), float(line[3])]
  Area           = float(line[4])
  stnID          = int(line[6])
  rivName        = line[7]
  stnName        = line[8]
  lstnID.append(stnID)
#--------------------------------------
da2dat = {}
for idat, stnID in enumerate(lstnID):
  rootDir  = "/tank/utsumi/out/TLSM"
  figDir   = rootDir + "/%s.%s.%02dc/fig"%(PRJ,RUN,ntag)
  figname  = figDir + "/plot.stack.%s.%s.png"%(var,stnID)
  a2fig    = Image.open(figname)
  a2array  = asarray(a2fig)[iyfig:eyfig, ixfig:exfig] 
  da2dat[idat] = a2array

da2dat[-9999] = da2dat[0]*0.0+255.

nlargefigs = int(ceil(float(len(lstnID))/9))
for i in range(len(lstnID), nlargefigs*9):
  da2dat[i] = da2dat[-9999]

for i in range(nlargefigs):
  a2line1 = hstack([da2dat[i*9+0], da2dat[i*9+1], da2dat[i*9+2]])
  a2line2 = hstack([da2dat[i*9+3], da2dat[i*9+4], da2dat[i*9+5]])
  a2line3 = hstack([da2dat[i*9+6], da2dat[i*9+7], da2dat[i*9+8]])

  a2oarray = vstack([a2line1, a2line2, a2line3])
  oimg     = Image.fromarray(uint8(a2oarray))
  oPath    = figDir + "/join.plot.stack.%s.%02d.png"%(var,i)
  oimg.save(oPath)
  print oPath


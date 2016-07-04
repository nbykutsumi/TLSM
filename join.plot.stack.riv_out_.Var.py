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

thnrmse = 0.5
#-- load Target Station List -------
listDir = "/tank/utsumi/data/TLSM/GRDC_Station"
#TargetListName  = listDir + "/Target.over10yr100000km2.csv"
TargetListName  = listDir + "/TargetStations.np.one.Aft1993.100000km2.filtered.3.csv"
f=open(TargetListName, "r")
lines = f.readlines()
f.close()
ltarget   = []
lrivnum   = []
dstnID    = {}
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
  lrivnum.append(rivnum)
  dstnID[rivnum] = stnID
#--------------------------------------
da2dat = {}
for i, rivnum in enumerate(lrivnum):
  rootDir  = "/tank/utsumi/out/TLSM"
  figDir   = rootDir + "/%s.%s.%02dc/fig"%(PRJ,RUN,ntag)
  #--- Prcp ---
  figname  = figDir + "/stack.Basin.PRCP.%04d.png"%(rivnum)
  a2fig    = Image.open(figname)
  a2array1 = asarray(a2fig)[iyfig:eyfig, ixfig:exfig]

  #--- Var  ---
  figname  = figDir + "/plot.stack.%s.%s.png"%(var,dstnID[rivnum])
  a2fig    = Image.open(figname)
  a2array2 = asarray(a2fig)[iyfig:eyfig, ixfig:exfig]
  #------------
  a2array  = vstack([a2array1,a2array2])
  da2dat[i]= a2array


da2dat[-9999] = da2dat[0]*0.0+255.

nlargefigs = int(ceil(float(len(lrivnum))/6))
for i in range(len(lrivnum), nlargefigs*6):
  da2dat[i] = da2dat[-9999]  


for i in range(nlargefigs):
  a2line1 = hstack([da2dat[i*6+0], da2dat[i*6+1], da2dat[i*6+2]])
  a2line2 = hstack([da2dat[i*6+3], da2dat[i*6+4], da2dat[i*6+5]])

  a2oarray = vstack([a2line1, a2line2])
  oimg     = Image.fromarray(uint8(a2oarray))
  oPath    = figDir + "/join.plot.stack.2Vars.%02d.png"%(i)
  oimg.save(oPath)
  print oPath


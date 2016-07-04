import Image
from numpy import *
import myfunc.IO.GRDC as GRDC

PRJ  = "JR55"
RUN  = "____"
ntag = 5
crd  = "np"
res  = "one"

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
  #--- Var1 ---
  figname  = figDir + "/stack.Basin.PRCP.%04d.png"%(rivnum)
  a2fig    = Image.open(figname)
  a2array1 = asarray(a2fig)[iyfig:eyfig, ixfig:exfig]

  #--- Var2  ---
  figname  = figDir + "/stack.Basin.%s.%04d.png"%("Evap____",rivnum)
  a2fig    = Image.open(figname)
  a2array2 = asarray(a2fig)[iyfig:eyfig, ixfig:exfig]

  #--- Var3  ---
  figname  = figDir + "/stack.Basin.%s.%04d.png"%("Qtot____",rivnum)
  a2fig    = Image.open(figname)
  a2array3 = asarray(a2fig)[iyfig:eyfig, ixfig:exfig]

  #--- Var4  ---
  figname  = figDir + "/plot.stack.%s.%s.png"%("riv_out_",dstnID[rivnum])
  a2fig    = Image.open(figname)
  a2array4 = asarray(a2fig)[iyfig:eyfig, ixfig:exfig]
  #------------
  a2array  = vstack([a2array1,a2array2,a2array3,a2array4])
  da2dat[i]= a2array


da2dat[-9999] = da2dat[0]*0.0+255.

nlargefigs = int(ceil(float(len(lrivnum))/3))
for i in range(len(lrivnum), nlargefigs*3):
  da2dat[i] = da2dat[-9999]  


for i in range(nlargefigs):
  a2line1 = hstack([da2dat[i*3+0], da2dat[i*3+1], da2dat[i*3+2]])

  a2oarray = a2line1
  oimg     = Image.fromarray(uint8(a2oarray))
  oPath    = figDir + "/join.plot.stack.4Vars.%02d.png"%(i)
  oimg.save(oPath)
  print oPath


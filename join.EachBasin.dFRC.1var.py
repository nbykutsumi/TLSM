import Image
from numpy import *
import myfunc.IO.GRDC as GRDC
import UtilTLSM

PRJ  = "JR55"
RUN  = "____"
ntag = 5
crd  = "np"
res  = "one"
#*** Figure para *********
iyfig  = 1  # top
eyfig  = -1  # bottom
ixfig  = 1
exfig  = -1

thnrmse= 0.5
var    = "RIVOUT-PRCP"
#-----------------------------------
def load_a2propfig(var, itag):
  rootDir  = "/tank/utsumi/out/TLSM"
  figDir   = rootDir + "/%s.%s.%02dc/fig"%(PRJ,RUN,ntag)
  #--- "PRCP" ----
  if var in ["PRCP","Evap____","Qtot____","SoilMois","riv_out_"]:
    figname  = figDir + "/map.prop.%s.%04d.%s.png"%(var,rivnum,ltag[itag])
  else:
    print "check var",var

  a2fig    = Image.open(figname)
  return a2fig
#-----------------------------------
def load_a2dFRCfig(var,itag):
  # var: RIVOOUT-QTOT,  QTOT-PRCP
  rootDir  = "/tank/utsumi/out/TLSM"
  figDir   = rootDir + "/%s.%s.%02dc/fig"%(PRJ,RUN,ntag)
  figname  = figDir + "/dFRC.%s.%04d.%s.png"%(var,rivnum,ltag[itag])
  a2fig    = Image.open(figname)
  return a2fig
#-----------------------------------

#-- load Target Station List -------
listDir = "/tank/utsumi/data/TLSM/GRDC_Station"
#TargetListName  = listDir + "/Target.over10yr100000km2.csv"
TargetListName  = listDir + "/TargetStations.np.one.Aft1993.100000km2.filtered.3.csv"
f=open(TargetListName, "r")
lines = f.readlines()
f.close()
ltarget   = []
lrivnum   = []
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
#--------------------------------------
ltag     = UtilTLSM.ret_ltag(ntag)
for rivnum in lrivnum:
#for rivnum in [58]:
  #-----------------
  ldFrc   = []
  for itag in range(ntag):
    #--- load dFRC ---
    a2fig    = load_a2dFRCfig(var,itag)
    a2array  = asarray(a2fig)[iyfig:eyfig, ixfig:exfig] 
    ldFrc.append(a2array)

  #-----------------
  a2line1  = hstack(ldFrc)
  a2oarray = a2line1
  oimg     = Image.fromarray(uint8(a2oarray))

  rootDir  = "/tank/utsumi/out/TLSM"
  figDir   = rootDir + "/%s.%s.%02dc/fig"%(PRJ,RUN,ntag)
  oPath    = figDir + "/join.EachBasin.dFRC.%s.%04d.png"%(var,rivnum)
  oimg.save(oPath)
  print oPath


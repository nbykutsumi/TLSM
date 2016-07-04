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
  figname  = figDir + "/dFRC.RIVOUT-QTOT.0001.ms.png"
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
  ldFrc1   = []
  ldFrc2   = []
  for itag in range(ntag):
    #--- load ----
    #--- dFRC Qtot-PRCP ---
    a2fig    = load_a2dFRCfig("QTOT-PRCP",itag)
    a2array  = asarray(a2fig)[iyfig:eyfig, ixfig:exfig] 
    ldFrc1.append(a2array)
    #--- dFRC RIVOUT-QTOT ---
    a2fig    = load_a2dFRCfig("RIVOUT-QTOT",itag)
    a2array  = asarray(a2fig)[iyfig:eyfig, ixfig:exfig] 
    ldFrc2.append(a2array)

  #-----------------
  a2line1 = hstack(lFrcPrcp)
  a2line2 = hstack(lFrcQtot)
  a2line3 = hstack(lFrcRivo)
  a2line4 = hstack(ldFrc1)
  a2line5 = hstack(ldFrc2)

  a2oarray = vstack([a2line1,a2line2,a2line3,a2line4,a2line5])
  oimg     = Image.fromarray(uint8(a2oarray))

  rootDir  = "/tank/utsumi/out/TLSM"
  figDir   = rootDir + "/%s.%s.%02dc/fig"%(PRJ,RUN,ntag)
  oPath    = figDir + "/join.EachBasin.%04d.png"%(rivnum)
  oimg.save(oPath)
  print oPath


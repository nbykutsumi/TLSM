from numpy import *
from datetime import datetime
from collections import deque
import myfunc.util as util
import myfunc.IO.GRDC as GRDC
import H08, ConstH08
import matplotlib.pyplot as plt

iYM    = [1990,1]
#eYM    = [1999,12]
eYM    = [2009,12]
#iYM    = [2000,1]
#eYM    = [2000,12]
lYM    = util.ret_lYM(iYM,eYM)
lMon   = range(1,12+1)
#PRJ="JR55"
#PRJ="GPCP"
#PRJ="GSMP"
PRJ = "JR55" #"JR55","GPCP","GSMP"]
RUN="____"
ntag = 5
crd  = "np"
res  = "one"
var  = "riv_out_"
#var  = "PRCP"
model="JRA55"

if res=="one":
  ny,nx  = 180,360

dunit = {
        #"riv_out_": "1000 m^3/s"
        "riv_out_": "mm/day"
        ,"PRCP"    : "mm/day"
        }

dMonName={1:"Jan",2:"Feb",3:"Mar",4 :"Apr",5 :"May",6 :"Jun"
         ,7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

araPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_ara_/rivara.GSWP2.one"
a2upara   = fromfile(araPath, float32).reshape(ny,nx)   # m^2

rivnumPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_num_/rivnum.GSWP2.one"
a2rivnum = fromfile(rivnumPath, float32).reshape(ny,nx)

H08     = H08.H08(prj=PRJ, run=RUN, res=res)
CH08    = ConstH08.ConstH08()
#--- load tag list ------------------
dirTaglist  = CH08.path_TagH08(DTime=datetime(1900,1,1), model=model, wnflag="nn", nclass=ntag, res=res)[0]
pathTaglist = dirTaglist + "/TAGS.txt"
f    =open(pathTaglist, "r")
ltag = [s.strip() for s in f.readlines()]
f.close()

dtag = {}
for itag in range(ntag):
  dtag[itag] = ltag[itag]


##-- load GRDC Station list ---------
grdc     = GRDC.GRDC()
mylist   = grdc.loadMyList(crd=crd, res=res)

#-- load Target Station List -------
listDir = "/tank/utsumi/data/TLSM/GRDC_Station"
#TargetListName  = listDir + "/Target.over10yr100000km2.csv"
#TargetListName  = listDir + "/TargetStations.np.one.Aft1993.100000km2.filtered.1.csv"
#TargetListName  = listDir + "/TargetStations.np.one.Aft1993.100000km2.filtered.2.csv"
TargetListName  = listDir + "/TargetStations.np.one.Aft1993.100000km2.filtered.3.csv"
f=open(TargetListName, "r")
lines = f.readlines()
f.close()
ltarget   = []
lstnID    = []
dAraModel = {}
dAraObs   = {}
for sline in lines[1:]:
  line           = sline.strip().split(",")
  #stnID          = int(line[5])  # filtered.1.csv

  stnID          = int(line[6])  # filtered.2 and 3
  AraModel       = float(line[4]) *1.e+6   # km^2 --> m^2
  AraObs         = float(line[11]) *1.e+6  # km^2 --> m^2
  dAraModel[stnID] = AraModel
  dAraObs  [stnID] = AraObs

  lstnID.append(stnID)

#-- load H08 variable --------------
da3var  = {}
for itag in range(ntag):
  da3var[itag]  = empty([len(lYM),ny,nx], float32)

for i,YM in enumerate(lYM):
  Year, Mon = YM
  a3in = H08.loadTagVarMon(var, ntag, Year, Mon)
  for itag in range(ntag):
    da3var[itag][i] = a3in[itag]
#-----------------------------------
da3var[-1] = zeros([len(lYM), ny, nx],float32)
for itag in range(ntag):
  da3var[-1] = da3var[-1] + da3var[itag]

#-- convert unit for calc ----
if   var == "riv_out_":
  coef = 1.0e-3  # kg/s --> m3/s 

elif var == "PRCP":
  coef = 60*60*24. # mm/day

for itag in [-1] + range(ntag):
  da3var[itag] = da3var[itag] * coef



for stnID in lstnID:
#for stnID in lstnID[0:1]:
  #-- load GRDC -------------
  if var == "riv_out_":
    grdc = GRDC.GRDC()
    #stnID = 4127800
    #stnID = 2181900
    lYMobs, lobs = grdc.loadMonthly(stnID, iYM=iYM, eYM=eYM)
    lobs  = ma.masked_less(lobs,0.0)

    dlobsOrg = {} 
    for itime,YM in enumerate(lYMobs):
      Year, Mon = YM
      vobs      = lobs[itime]
      if dlobsOrg.has_key(Mon):
        dlobsOrg[Mon].append(vobs)
      else:
        dlobsOrg[Mon] = deque([vobs])
  #-- extract from 3-D array --
  iy,ix   = mylist.dyx[stnID]
  dlsimOrg   = {}
  for itag in [-1] + range(ntag):

    for itime,YM in enumerate(lYM):
      Year, Mon = YM
      #----------
      vsim  = da3var[itag][itime][iy,ix] 
      if dlsimOrg.has_key((itag,Mon)):
        dlsimOrg[itag,Mon].append(vsim)
      else:
        dlsimOrg[itag,Mon] = deque([vsim] )

  #-- make climatology simulation --
  dlsim = {} 
  for itag in range(ntag):
    for Mon in lMon:
      if dlsim.has_key(itag):
        dlsim[itag].append(array(dlsimOrg[itag,Mon]).mean())
      else:
        dlsim[itag] = [array(dlsimOrg[itag,Mon]).mean()]

    dlsim[itag] = array(dlsim[itag])
  #-- make climatology for obs ----- 
  lobs = []
  for Mon in lMon:
    vobs = ma.masked_invalid(array(dlobsOrg[Mon])).mean()
    lobs.append(vobs)

  lobs = array(lobs)
  #-- make stack ------------
  dlsimstack = {}
  for itag in range(ntag):
    if itag==0:
      dlsimstack[itag] = dlsim[itag]
    else:
      dlsimstack[itag] = dlsimstack[itag-1] + dlsim[itag]
  
  #*********** Figure **********************
  dcolor   = {"tc":"r", "c":"royalblue","fbc":"lime","ms":"orange","ot":"gray"}
  
  #------------------
  lx       = lMon
  figplot  = plt.figure(figsize=(3,1.5))
  axplot   = figplot.add_axes([0.12, 0.23, 0.83, 0.65])


  #** unit coef for figure ***** 
  if   var == "riv_out_":
    if dunit[var]=="mm/day":
      coef     = 1.0e+3                   # m^3/s    --> kg/s 
      coef     = coef / dAraModel[stnID]  # kg/s     --> kg/m^2/s
      coef     = coef * 60*60*24.         # kg/m^2/s --> kg/m^2/day = mm/m^2/day
      coef_obs = 1.0e+3                   # m^3/s    --> kg/s 
      coef_obs = coef_obs / dAraObs[stnID]  # kg/s     --> kg/m^2/s
      coef_obs = coef_obs * 60*60*24.         # kg/m^2/s --> kg/m^2/day = mm/m^2/day

    else:
      coef     = 1.e-3  # m^3/s --> 1000 m^3/s
      coef_obs = 1.e-3  # m^3/s --> 1000 m^3/s

  elif var == "PRCP":
    coef     = 1.0    # mm/day

  #** stack plot ****
  for itag in range(ntag)[::-1]:
    tag    = dtag[itag]
    axplot.fill_between(lx, 0, dlsimstack[itag]*coef, color=dcolor[tag])
  
  #** obs plot *****
  if var == "riv_out_":
    axplot.plot(lx, lobs*coef_obs, "-", linewidth=2, color="k")
  
  #** x-labels ******
  xlabels  = ["%s"%(dMonName[Mon]) for Mon in lMon]
  #xlabels  = ["%04d-%s"%(Year,Mon) for Year in zip(*lYM)[0] for Mon in zip(*lYM)[1]]
  
  #** x-ticks *****
  axplot.xaxis.set_ticks(lx)
  axplot.xaxis.set_ticklabels(xlabels, minor=False, fontsize=10, rotation=90)
  
  #** axis limit **
  axplot.set_xlim([lx[0],lx[-1]])
  axplot.set_ylim(bottom=0)
  
  #** title *******
  stnName  = mylist.dstnName[stnID]
  rivName  = mylist.drivName[stnID]
  rivnum   = mylist.drivnum[stnID]
  stitle   = "%s(%d) / %s(%d)"%(rivName, rivnum, stnName, stnID) 
  plt.title(stitle, fontsize=10)
  #** text ******** 
  x_text = 0.98
  y_text = 0.98
  stext  = "%s[%s]"%(var, dunit[var])
  ha     = "right"
  va     = "top"
  axplot.text(x_text, y_text, stext, transform= axplot.transAxes, ha=ha, va=va)
  
  #--- save ---
  rootDir  = "/tank/utsumi/out/TLSM"
  figDir   = rootDir + "/%s.%s.%02dc/fig"%(PRJ,RUN,ntag)
  util.mk_dir(figDir)
  figname  = figDir + "/clim.stack.%s.%s.png"%(var,stnID)
  figplot.savefig(figname)
  print figname




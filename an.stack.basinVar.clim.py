from numpy import *
from datetime import datetime
from collections import deque
import sys
import myfunc.util as util
import myfunc.IO.GRDC as GRDC
import H08, ConstH08
import matplotlib.pyplot as plt

iYM    = [1990,1]
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
#var  = "PRCP"
#var  = "Evap____"
#var  = "Qtot____"
#var  = "SoilMois"
lvar  = ["PRCP","Evap____","Qtot____","SoilMois"]
#lvar  = ["Evap____"]

model="JRA55"

if res=="one":
  ny,nx  = 180,360

dunit = {"riv_out_": "1000 m^3/s"
        ,"PRCP"    : "mm/day"
        ,"Evap____": "mm/day"
        ,"Qtot____": "mm/day"
        ,"SoilMois": "kg/m^2"
        }

dMonName={1:"Jan",2:"Feb",3:"Mar",4 :"Apr",5 :"May",6 :"Jun"
         ,7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

araPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_ara_/rivara.GSWP2.one"
a2ara   = fromfile(araPath, float32).reshape(ny,nx)
a2ara   = a2ara/1.e+6   # km^2

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
lrivnum   = []
drivName  = {}
for sline in lines[1:]:
  line           = sline.strip().split(",")
  #rivnum          = int(line[0])  # filtered.1.csv
  #rivName         = line[7]
  rivnum          = int(line[1])  # filtered.2 & 3
  rivName         = line[8]

  lrivnum.append(rivnum)
  if not drivName.has_key(rivnum):
    drivName[rivnum] = rivName

#***** start var loop *************************
for var in lvar:
  #-- load H08 variable --------------
  da2var  = {}
  for itag in range(ntag):
    for Mon in lMon:
      da2var[itag,Mon]  = zeros([ny,nx], float32)
 
  dtimes  = {}
  for i,YM in enumerate(lYM):
    Year, Mon = YM
    #----------
    if dtimes.has_key(Mon):
      dtimes[Mon] = dtimes[Mon] + 1
    else:
      dtimes[Mon] = 1
    #----------
    a3in = H08.loadTagVarMon(var, ntag, Year, Mon)
    for itag in range(ntag):
      da2var[itag,Mon] = da2var[itag,Mon] + a3in[itag]
  #-----------------------------------
  for itag in range(ntag):
    for Mon in lMon:
      da2var[itag, Mon] = da2var[itag, Mon] / dtimes[Mon]

  #---- for total --------------------
  for Mon in lMon:
    da2var[-1,Mon] = zeros([ny, nx],float32)
    for itag in range(ntag):
      da2var[-1,Mon] = da2var[-1,Mon] + da2var[itag,Mon]
  
  #-- convert unit ----
  if   var == "riv_out":
    coef = 1.0e-3  # kg/s --> m3/s 
  elif var == "PRCP":
    coef = 60*60*24. # mm/day
  elif var == "Evap____":
    coef = 60*60*24. # mm/day
  elif var == "Qtot____":
    coef = 60*60*24. # mm/day
  elif var == "SoilMois":
    coef = 1.0       # kg/m^2 --> kg/m^2
  else:
    print "coef not defined", var
    sys.exit()
  
  for itag in [-1] + range(ntag):
    for Mon in lMon:
      da2var[itag,Mon] = da2var[itag,Mon] * coef
  
  #-- extract from 3-D array --
  for rivnum in lrivnum:
  #for rivnum in [3]:
    a2mask  = ma.masked_not_equal(a2rivnum, rivnum)
  
    dlsim   = {}
    for itag in [-1] + range(ntag):
      dlsim[itag] = deque([])
    
      for Mon in lMon:
        vsim  = ma.masked_where(a2mask.mask, da2var[itag,Mon]).mean()
        dlsim[itag].append( vsim )
    
      dlsim[itag] = array(dlsim[itag])

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
    figplot  = plt.figure(figsize=(3,1.5))
    axplot   = figplot.add_axes([0.15, 0.23, 0.83, 0.65])
  
  
    #** figure unit coef ***** 
    if   var == "riv_out_":
      coef = 1.e-3  # m^3/s --> 1000 m^3/s
    elif var == "PRCP":
      coef = 1.0    # mm/day
    elif var == "Evap____":
      coef = 1.0    # mm/day
    elif var == "Qtot____":
      coef = 1.0    # mm/day
    elif var == "SoilMois":
      coef = 1.0    # mm/day
    else:
      print "figure unit coef not defined"
      sys.exit()
  
    #** line plot ****
    lx       = range(len(lMon))
    for itag in range(ntag)[::-1]:
      tag    = dtag[itag]
      axplot.fill_between(lx, 0, dlsimstack[itag]*coef, color=dcolor[tag])
    
    #** x-labels ******
    xlabels  = ["%s"%(dMonName[Mon]) for Mon in lMon]
    
    #** x-ticks *****
    axplot.xaxis.set_ticks(lx)
    axplot.xaxis.set_ticklabels(xlabels, minor=False, fontsize=10, rotation=90)
    
    #** axis limit **
    axplot.set_xlim([lx[0],lx[-1]])
    axplot.set_ylim(bottom=0)
    
    #** title *******
    rivName  = drivName[rivnum]
    stitle   = "%s(%d)"%(rivName, rivnum) 
    plt.title(stitle, fontsize=10)
    #** text ******** 
    x_text = 0.98
    y_text = 0.98
    stext  = "basin average %s[%s]"%(var, dunit[var])
    ha     = "right"
    va     = "top"
    axplot.text(x_text, y_text, stext, transform= axplot.transAxes, ha=ha, va=va, fontsize=9)
    
    #--- save ---
    rootDir  = "/tank/utsumi/out/TLSM"
    figDir   = rootDir + "/%s.%s.%02dc/fig"%(PRJ,RUN,ntag)
    util.mk_dir(figDir)
    figname  = figDir + "/clim.stack.Basin.%s.%s.png"%(var,rivnum)
    figplot.savefig(figname)
    print figname




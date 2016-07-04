from numpy import *
from datetime import datetime, timedelta
import myfunc.fig.Fig as Fig
import myfunc.util as util
import myfunc.IO.GRDC as GRDC
import ConstH08
import H08
import UtilTLSM
iYM  = [1990,1]
eYM  = [1990,1]
lYM  = util.ret_lYM(iYM, eYM)

model= "JRA55"
PRJ  = "JR55"
RUN  = "____"
crd  = "np"
res  = "one"
h08  = H08.H08(prj=PRJ, run=RUN, res=res)
CH08 = ConstH08.ConstH08()
miss = -9999.
lvar  = ["PRCP","Evap____","Qtot____","SoilMois","riv_out_"]
#lvar  = ["Evap____"]

ntag = 5
ny,nx = h08.ny, h08.nx
a1lat = h08.Lat
a1lon = h08.Lon

#dunit = {"riv_out_": "1000 m^3/s"
#        ,"PRCP"    : "mm/day"
#        ,"Evap____": "mm/day"
#        ,"Qtot____": "mm/day"
#        ,"SoilMois": "kg/m^2"
#        }

dunit = {"riv_out_": "proportion"
        ,"PRCP"    : "proportion"
        ,"Evap____": "proportion"
        ,"Qtot____": "proportion"
        ,"SoilMois": "proportion"
        }

#--- load const maps ----------------
a2rivnum = h08.load_H08const("riv_num_")

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
TargetListName  = listDir + "/TargetStations.np.one.Aft1993.100000km2.filtered.2.csv"
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
  rivnum          = int(line[1])  # filtered.2.csv
  rivName         = line[8]

  lrivnum.append(rivnum)
  if not drivName.has_key(rivnum):
    drivName[rivnum] = rivName

#******************************
da2clim = {}
for var in lvar:
  #-- load H08 variable --------------
  da2var = {}
  for itag in range(ntag):
    da2var[itag]  = zeros([ny,nx], float32)

  for i,YM in enumerate(lYM):
    Year, Mon = YM
    a3in = h08.loadTagVarMon(var, ntag, Year, Mon)
    for itag in range(ntag):
      da2var[itag] = da2var[itag] + a3in[itag]

  for itag in range(ntag):
    da2var[itag] = da2var[itag] / len(lYM)
  #-----------------------------------
  da2var[-1] = zeros([ny, nx],float32)
  for itag in range(ntag):
    da2var[-1] = da2var[-1] + da2var[itag]


  for itag in [-1] + range(ntag):
    da2clim[var,itag] = da2var[itag]

  #****** proportion ************
  da2prop = {}
  for itag in range(ntag):
    da2prop[itag] = ma.masked_where(da2var[-1]==0.0, da2var[itag]) / da2var[-1]
    da2prop[itag] = da2prop[itag].filled(0.0)


diSoilM = {}
deSoilM = {}
iYear,iMon  = iYM
eYear,eMon  = eYM
iDTime = datetime(iYear,iMon,1,0)
eDTime = datetime(eYear,eMon,31,0)

iSoilTot = h08.load_H08var("SoilMois",iDTime)
eSoilTot = h08.load_H08var("SoilMois",eDTime)
iFrcSoil = h08.load_H08var("FrcSoilM",iDTime)
eFrcSoil = h08.load_H08var("FrcSoilM",eDTime)

for itag in range(ntag):
  diSoilM[itag]   = iSoilTot * iFrcSoil[itag]
  deSoilM[itag]   = eSoilTot * eFrcSoil[itag]

diSoilM[-1] = iSoilTot
deSoilM[-1] = eSoilTot


totalsec = (eDTime - iDTime).total_seconds()
dVal = {}
for itag in [-1] + range(ntag):
  dVal[itag] = (da2clim["PRCP",itag] - da2clim["Evap____",itag] - da2clim["Qtot____",itag])*totalsec - (deSoilM[itag] - diSoilM[itag])
  #dVal[itag] = (da2clim["PRCP",itag] - da2clim["Evap____",itag] - da2clim["Qtot____",itag])*totalsec

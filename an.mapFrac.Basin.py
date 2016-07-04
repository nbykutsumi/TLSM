from numpy import *
from datetime import datetime
import myfunc.fig.Fig as Fig
import myfunc.util as util
import myfunc.IO.GRDC as GRDC
import ConstH08
import H08
import UtilTLSM
iYM  = [1990,1]
eYM  = [2009,12]
#iYM  = [2000,1]
#eYM  = [2000,12]

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
#lvar  = ["PRCP"]

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
  rivnum          = int(line[1])  # filtered.2.csv
  rivName         = line[8]

  lrivnum.append(rivnum)
  if not drivName.has_key(rivnum):
    drivName[rivnum] = rivName

#******************************
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

  #****** proportion ************
  da2prop = {}
  for itag in range(ntag):
    da2prop[itag] = ma.masked_where(da2var[-1]==0.0, da2var[itag]) / da2var[-1]
    da2prop[itag] = da2prop[itag].filled(0.0)

  #*********** Figure ***********
  ltag     = UtilTLSM.ret_ltag(ntag)
  dBBox = CH08.ret_rivnumBBox()
  
  #for rivnum in lrivnum:
  for rivnum in [0]:
  #for rivnum in [58]:
    if rivnum == 0:
      a2rivmask = ones([ny,nx])
    else:
      a2rivmask = ma.masked_where(a2rivnum !=rivnum, ones([ny,nx])).filled(miss)
  
    for itag in range(ntag):
    #for itag in [1]:
      print var,rivnum,itag
      tag     = ltag[itag]
      a2figdat  = da2prop[itag]
      #--- BBox -------------
      if rivnum == 0:
        BBox    = [[-90,-180],[90,180]]
      else: 
        BBox    = dBBox[rivnum]
      #--- figname ----------
      rootDir  = "/tank/utsumi/out/TLSM"
      figDir   = rootDir + "/%s.%s.%02dc/fig"%(PRJ,RUN,ntag)
      util.mk_dir(figDir)
      figname  = figDir + "/map.prop.%s.%04d.%s.png"%(var,rivnum,ltag[itag])
      cbarname = figDir + "/cbar.prop.png"
  
      #--- colorbar ---------
      bnd     = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
      mycm    = "jet"
  
      #--- title ------------
      if rivnum ==0:
        stitle  = ""
      else:
        stitle  = "%s (%04d)"%(drivName[rivnum], rivnum) + "\n"
        stitle  = stitle + "%s %s %s"%(var, ltag[itag], dunit[var])

      #--- figsize ----------
      if rivnum ==0:
        figsize = (6,3) 
      else:
        figsize = (3,3)
      #--- plot ---
      Fig.DrawMap(a2figdat, a1lat, a1lon, BBox=BBox,figname=figname, a2shade=a2rivmask, bnd=bnd, mycm=mycm, cbarname=cbarname, symm=True, lowest_white=True, figsize=figsize,lonlatfontsize=7, lonrotation=0, stitle=stitle)
      print figname
  
  

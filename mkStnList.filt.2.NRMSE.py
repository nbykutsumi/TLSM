from numpy import *
from datetime import datetime
from collections import deque
import myfunc.util as util
import myfunc.IO.GRDC as GRDC
import H08, ConstH08
#import matplotlib.pyplot as plt

iYM    = [1990,1]
eYM    = [2010,12]
#iYM    = [2000,1]
#eYM    = [2004,12]
lYM    = util.ret_lYM(iYM,eYM)
#PRJ="JR55"
#PRJ="GPCP"
#PRJ="GSMP"
PRJ = "JR55" #"JR55","GPCP","GSMP"]
RUN="____"
ntag = 5
crd  = "np"
res  = "one"
var  = "riv_out_"
model="JRA55"
miss = -9999.

thNRMSE = 0.5

if res=="one":
  ny,nx  = 180,360

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
TargetListName  = listDir + "/TargetStations.np.one.Aft1993.100000km2.filtered.1.csv"
f=open(TargetListName, "r")
lines = f.readlines()
f.close()
lstnID    = []
dsline    = {}

slabels   = lines[0]

for sline in lines[1:]:
#for sline in lines[1:2]:
  line           = sline.strip().split(",")
  stnID          = int(line[5])
  lstnID.append(stnID)
  dsline[stnID]  = sline
 
#-- load H08 variable --------------
da3var  = {}
for itag in range(ntag):
  da3var[itag]  = empty([len(lYM),ny,nx], float32)

for i,YM in enumerate(lYM):
  Year, Mon = YM
  a3in = H08.loadTagVarMon(var, ntag, Year, Mon)
  for itag in range(ntag):
    da3var[itag][i] = a3in[itag]
#--------------------
da3var[-1] = zeros([len(lYM), ny, nx],float32)
for itag in range(ntag):
  da3var[-1] = da3var[-1] + da3var[itag]

#-- convert unit ----
coef = 1.0e-3  # kg/s --> m3/s 
for itag in [-1] + range(ntag):
  da3var[itag] = da3var[itag] * coef


sout = "NRMSE" + "," + slabels
lstnID  = sort(lstnID)
for stnID in lstnID:
  #-- load GRDC -------------
  grdc = GRDC.GRDC()
  lYM, lobs = grdc.loadMonthly(stnID, iYM=iYM, eYM=eYM)
  lobs  = ma.masked_less(lobs,0.0)
  
  #-- extract from 3-D array --
  iy,ix  = mylist.dyx[stnID]
  lsim   = deque([])
  for itime in range(len(lYM)):
    vsim  = da3var[-1][itime][iy,ix] 
    lsim.append( vsim )
  
  lsim = array(lsim)
  #---------------
  nrmse = float(sqrt((lsim - lobs)**2).mean()/ lobs.mean())
  if isnan(nrmse):
    nrmse = miss
  #---------------
  if ((nrmse <0)or(nrmse > thNRMSE)):
    print "skip",nrmse
    continue
  #---------------
  sout = sout + "%s"%(nrmse) + "," + dsline[stnID]

oPath = TargetListName[:-6] + ".2.csv"
f     = open(oPath, "w")
f.write(sout)
f.close()
print oPath
 


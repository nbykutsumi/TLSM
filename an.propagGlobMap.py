from numpy import *
import myfunc.fig.Fig as Fig
import myfunc.util as util
import ConstH08
#import myfunc.IO.GRDC as GRDC
import H08

iYM  = [1990,1]
eYM  = [1999,12]
lYM  = util.ret_lYM(iYM, eYM)

PRJ  = "JR55"
RUN  = "____"
crd  = "np"
res  = "one"

h08  = H08.H08(prj=PRJ, run=RUN, res=res)
#grdc = GRDC.GRDC()
#mylist = grdc.loadMyList(crd=crd, res=res)

vartype = "FRC"
#vartype = "MMPD"

ntag = 5
ny,nx = h08.ny, h08.nx
a1lat = h08.Lat
a1lon = h08.Lon
BBox  = [[-80,-180],[80,180]]
lndaraPath= "/tank/utsumi/H08/H08_20130501/map/dat/lnd_ara_/lndara.GSWP2.one"
a2lndara  = fromfile(lndaraPath, float32).reshape(ny,nx)

uparaPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_ara_/rivara.GSWP2.one"
a2upara   = fromfile(uparaPath, float32).reshape(ny,nx)

numPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_num_/rivnum.GSWP2.one"
a2num   = fromfile(numPath, float32).reshape(ny,nx)

dPrcpDir  = {"JR55": "/tank/utsumi/data/H08/ELSE.JRA55.L1_01u"}

ptagDir ="/tank/utsumi/tag.mask/JRA55.nn.%04dc.one"%(ntag)

dvarName= {"PRCP":"PRCP", "QTOT":"Qtot____", "RIVOUT":"riv_out_"}
#--- load list ----------
listDir = "/tank/utsumi/data/TLSM/GRDC_Station"
iPath   = listDir + "/TargetStations.np.one.Aft1993.100000km2.filtered.3.csv"
f       = open(iPath, "r")
lines   = f.readlines()
f.close()

lrivnum  = []
for sline in lines[1:]:
  line   = sline.split(",")
  rivnum = int(line[1])
  lrivnum.append(rivnum)

#--- rivmask -----------
a2rivmask = zeros([ny,nx],float32)
for rivnum in lrivnum:
  a2rivmask = ma.masked_where(a2num==rivnum, a2rivmask).filled(1.0)

#******************************
def ret_ltag(ntag):
  srcPath = "/tank/utsumi/tag.mask/JRA55.nn.%02dc.one/TAGS.txt"%(ntag)
  f=open(srcPath, "r")
  lines = f.readlines()
  f.close()
  return [s.strip() for s in lines]
#******************************

QTOT    = zeros([ntag,ny,nx],float32)
RIVOUT  = zeros([ntag,ny,nx],float32)
PRCP    = zeros([ntag,ny,nx],float32)
for Year,Mon in lYM:
  QTOT    = QTOT   + h08.loadTagVarMon(dvarName["QTOT"], ntag, Year, Mon)
  RIVOUT  = RIVOUT + h08.loadTagVarMon(dvarName["RIVOUT"], ntag, Year, Mon)
  PRCP    = PRCP   + h08.loadTagVarMon(dvarName["PRCP"], ntag, Year, Mon)

QTOT   = QTOT   / len(lYM)
RIVOUT = RIVOUT / len(lYM)
PRCP   = PRCP   / len(lYM)

if vartype == "FRC":
  FRCQTOT   = zeros([ntag,ny,nx],float32)
  FRCRIVOUT = zeros([ntag,ny,nx],float32)
  FRCPRCP   = zeros([ntag,ny,nx],float32)
  for itag in range(ntag):
    FRCQTOT[itag]   = ma.masked_where(QTOT.sum(axis=0)==0.0,   QTOT[itag])   / QTOT.sum(axis=0)
    FRCRIVOUT[itag] = ma.masked_where(RIVOUT.sum(axis=0)==0.0, RIVOUT[itag]) / RIVOUT.sum(axis=0)
    FRCPRCP[itag]   = ma.masked_where(PRCP.sum(axis=0)==0.0,   PRCP[itag])   / PRCP.sum(axis=0)
  
  dVAR1  = FRCQTOT   - FRCPRCP
  dVAR2  = FRCRIVOUT - FRCQTOT

elif vartype == "MMPD":
  RIVOUTMMPD   = zeros([ntag,ny,nx],float32)
  for itag in range(ntag):
    RIVOUTMMPD[itag] = ma.masked_where(a2lndara>1.0e+19, RIVOUT[itag]) / a2lndara * 60*60*24.

  QTOTMMPD = QTOT*60*60*24.
  PRCPMMPD = PRCP*60*60*24.

  dVAR1  = QTOTMMPD    - PRCPMMPD
  dVAR2  = RIVOUTMMPD  - QTOTMMPD


#*********** Figure ***********
ltag     = ret_ltag(ntag)
for itag in range(ntag):
  tag     = ltag[itag]
  cmap    = "bwr"
  if vartype == "FRC":
    vmin    = -0.5
    vmax    = +0.5
  elif vartype == "MMPD":
    vmin    = -5.0
    vmax    = +5.0

  rootDir  = "/tank/utsumi/out/TLSM"
  figDir   = rootDir + "/%s.%s.%02dc/fig"%(PRJ,RUN,ntag)
  util.mk_dir(figDir)

  #---- dVAR1 ---
  dVAR    = dVAR1

  #figname = sDir + "/d%s.QTOT-PRCP.%s.%s.tag%02d.png"%(vartype,PRJ, riv, itag)  
  #stitle  = "d%s QTOT - PRCP %s %s"%(vartype, riv, tag)

  a2in    = ma.masked_where(a2rivmask !=1.0,  dVAR[itag])
  stitle  = "d%s QTOT - PRCP %s"%(vartype, tag)

  figname = figDir + "/d%s.QTOT-PRCP.tag%02d.png"%(vartype, itag)  
  Fig.DrawMap(a2in=a2in, a1lat=a1lat, a1lon=a1lon, BBox=BBox, figname=figname, stitle=stitle, cmap="bwr",vmax=vmax, vmin=vmin, maskcolor="0.8")

  #---- dVAR2 ---
  dVAR    = dVAR2
  #a2in    = ma.masked_where(a2num !=drivnum[riv],  dVAR[itag])
  #figname = sDir + "/d%s.RIVOUT-QTOT.%s.%s.tag%02d.png"%(vartype, PRJ, riv, itag)  
  #stitle  = "d%s RIVOUT - QTOT %s %s"%(vartype, riv, tag)

  a2in    = ma.masked_where(a2rivmask !=1.0,  dVAR[itag])
  stitle  = "d%s RIVOUT - QTOT %s"%(vartype, tag)
  figname = figDir + "/d%s.RIVOUT-QTOT.tag%02d.png"%(vartype, itag)  

  Fig.DrawMap(a2in=a2in, a1lat=a1lat, a1lon=a1lon,  BBox=BBox, figname=figname, stitle=stitle, cmap="bwr",vmax=vmax, vmin=vmin, maskcolor="0.8")

  



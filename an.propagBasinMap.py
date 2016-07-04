from numpy import *
import myfunc.fig.Fig as Fig
import myfunc.util as util
import ConstH08
import H08
iYM  = [1990,1]
eYM  = [1999,12]
lYM  = util.ret_lYM(iYM, eYM)

PRJ  = "JR55"
RUN  = "____"
res  = "one"
h08  = H08.H08(prj=PRJ, run=RUN, res=res)
ch08 = ConstH08.ConstH08()
dBBox= ch08.ret_rivnumBBox()

vartype = "FRC"
#vartype = "MMPD"
miss = -9999.

ntag = 5
ny,nx = h08.ny, h08.nx
a1lat = h08.Lat
a1lon = h08.Lon

a2rivnum = h08.load_H08const("riv_num_")
a2lndara = h08.load_H08const("lnd_ara_")
a2upara  = h08.load_H08const("riv_ara_")

dPrcpDir  = {"JR55": "/tank/utsumi/data/H08/ELSE.JRA55.L1_01u"}

ptagDir ="/tank/utsumi/tag.mask/JRA55.nn.%04dc.one"%(ntag)

dvarName= {"PRCP":"PRCP", "QTOT":"Qtot____", "RIVOUT":"riv_out_"}
#******************************
def ret_ltag(ntag):
  srcPath = "/tank/utsumi/tag.mask/JRA55.nn.%02dc.one/TAGS.txt"%(ntag)
  f=open(srcPath, "r")
  lines = f.readlines()
  f.close()
  return [s.strip() for s in lines]
#******************************
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
  rivnum          = int(line[1])  # filtered.2.csv
  rivName         = line[8]

  lrivnum.append(rivnum)
  if not drivName.has_key(rivnum):
    drivName[rivnum] = rivName
#******************************
QTOT    = zeros([ntag,ny,nx],float32)
RIVOUT  = zeros([ntag,ny,nx],float32)
PRCP    = zeros([ntag,ny,nx],float32)
for Year,Mon in lYM:
  QTOT    = QTOT   + h08.loadTagVarMon(dvarName["QTOT"], ntag, Year, Mon)
  RIVOUT  = RIVOUT + h08.loadTagVarMon(dvarName["RIVOUT"], ntag, Year, Mon)
  PRCP    = PRCP   +  h08.loadTagVarMon(dvarName["PRCP"], ntag, Year, Mon)

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
  dVAR3  = FRCRIVOUT - FRCPRCP

elif vartype == "MMPD":
  RIVOUTMMPD   = zeros([ntag,ny,nx],float32)
  for itag in range(ntag):
    RIVOUTMMPD[itag] = ma.masked_where(a2lndara>1.0e+19, RIVOUT[itag]) / a2lndara * 60*60*24.

  QTOTMMPD = QTOT*60*60*24.
  PRCPMMPD = PRCP*60*60*24.

  dVAR1  = QTOTMMPD    - PRCPMMPD
  dVAR2  = RIVOUTMMPD  - QTOTMMPD
  dVAR3  = RIVOUTMMPD  - PRCPMMPD

#*********** Figure ***********
ltag     = ret_ltag(ntag)
for rivnum in lrivnum:
#for rivnum in lrivnum[0:1]:
  a2rivmask = ones([ny,nx],float32)*miss
  a2rivmask = ma.masked_where(a2rivnum==rivnum, a2rivmask).filled(1.0)

  for itag in range(ntag):
    tag     = ltag[itag]
    BBox    = dBBox[rivnum]
    cmap    = "bwr"
    if vartype == "FRC":
      vmin    = -0.5
      vmax    = +0.5
    elif vartype == "MMPD":
      vmin    = -5.0
      vmax    = +5.0
  
    rootDir  = "/tank/utsumi/out/TLSM"
    sDir    = rootDir + "/%s.%s.%02dc/fig"%(PRJ,RUN,ntag)
    util.mk_dir(sDir)

    #***************************
    #---- dVAR1 ---
    dVAR    = dVAR1
  
    a2in    = ma.masked_where(a2rivnum !=rivnum,  dVAR[itag])
    figname = sDir + "/d%s.QTOT-PRCP.%04d.%s.png"%(vartype,rivnum, ltag[itag])  
    #--- colorbar ---------- 
    if rivnum==lrivnum[0]:
      cbarname = sDir + "/cbar.d%s.QTOT-PRCP.png"%(vartype)
    else:
      cbarname = None

    if vartype == "FRC":
      bnd = [-0.2, -0.1, -0.05, -0.03, 0.03, 0.05, 0.1, 0.2]
    elif vartype == "MMPD":
      bnd = [-20, -10, -5, -1, 1,5,10,20,50,100] 

    mycm = "bwr"
    #----------------------- 
    stitle  = "%s %s"%(drivName[rivnum], tag)
    stitle  = stitle + "\n" + "d%s QTOT - PRCP"%(vartype)
  
  
    Fig.DrawMap(a2in=a2in, a1lat=a1lat, a1lon=a1lon, BBox=BBox, figname=figname, cbarname=cbarname, stitle=stitle, titlefontsize=12, mycm=mycm,figsize=(3,3), bnd=bnd, a2shade=a2rivmask)

    #***************************
    #---- dVAR2 ---
    dVAR    = dVAR2
    a2in    = ma.masked_where(a2rivnum !=rivnum,  dVAR[itag])
    figname = sDir + "/d%s.RIVOUT-QTOT.%04d.%s.png"%(vartype, rivnum, ltag[itag])  
    #--- colorbar ---------- 
    if rivnum==lrivnum[0]:
      cbarname = sDir + "/cbar.d%s.RIVOUT-QTOT.png"%(vartype)
    else:
      cbarname = None

    if vartype == "FRC":
      bnd = [-0.2, -0.1, -0.05, -0.03, 0.03, 0.05, 0.1, 0.2]
      mycm = "bwr"
    elif vartype == "MMPD":
      bnd = [1,5,10,20,50,100] 
      mycm = "Reds"
      #mycm = "bwr"

    #-----------------------
    stitle  = "%s %s"%(drivName[rivnum], tag)
    stitle  = stitle + "\n" + "d%s RIVOUT - QTOT"%(vartype)
  
    Fig.DrawMap(a2in=a2in, a1lat=a1lat, a1lon=a1lon,  BBox=BBox, figname=figname, cbarname=cbarname, stitle=stitle, titlefontsize=12, mycm=mycm, figsize=(3,3), bnd=bnd, a2shade=a2rivmask)
    print figname

    #***************************
    #---- dVAR3 ---
    dVAR    = dVAR3
    a2in    = ma.masked_where(a2rivnum !=rivnum,  dVAR[itag])
    figname = sDir + "/d%s.RIVOUT-PRCP.%04d.%s.png"%(vartype, rivnum, ltag[itag])  
    #--- colorbar ---------- 
    if rivnum==lrivnum[0]:
      cbarname = sDir + "/cbar.d%s.RIVOUT-PRCP.png"%(vartype)
    else:
      cbarname = None

    if vartype == "FRC":
      bnd = [-0.2, -0.1, -0.05, -0.03, 0.03, 0.05, 0.1, 0.2]
      mycm = "bwr"
    elif vartype == "MMPD":
      bnd = [1,5,10,20,50,100] 
      mycm = "Reds"
      #mycm = "bwr"

    #-----------------------
    stitle  = "%s %s"%(drivName[rivnum], tag)
    stitle  = stitle + "\n" + "d%s RIVOUT - PRCP"%(vartype)
  
    Fig.DrawMap(a2in=a2in, a1lat=a1lat, a1lon=a1lon,  BBox=BBox, figname=figname, cbarname=cbarname, stitle=stitle, titlefontsize=12, mycm=mycm, figsize=(3,3), bnd=bnd, a2shade=a2rivmask)
    print figname



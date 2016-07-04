from numpy import *
import matplotlib.pyplot as plt
import H08
import myfunc.util as util
import UtilTLSM

iYM = [1990,1]
#eYM = [1990,12]
eYM = [2010,12]
lYM = util.ret_lYM(iYM, eYM)

prj = "JR55"
run = "____"
res = "one"
ntag= 5
h08 = H08.H08(prj=prj, run=run, res=res)
ny  = h08.ny
nx  = h08.nx

a2rivnum = h08.load_H08const("riv_num")
a2lndara = h08.load_H08const("lnd_ara_")
ltag     = UtilTLSM.ret_ltag(ntag=ntag, model="JRA55", wnflag="nn", res=res)

vartype  = "FRC"
#vartype  = "MMPD"
#--- load tagged data --------
a3PRCP = zeros([ntag,ny,nx],float32)
a3QTOT = zeros([ntag,ny,nx],float32)

for YM in lYM:
  Year    = YM[0]
  Mon     = YM[1]
  a3prcp  = h08.loadTagVarMon("PRCP",ntag,Year,Mon)
  a3qtot  = h08.loadTagVarMon("Qtot____",ntag,Year,Mon)

  a3PRCP  = a3PRCP + a3prcp 
  a3QTOT  = a3QTOT + a3qtot

a3PRCP  = a3PRCP / len(lYM)
a3QTOT  = a3QTOT / len(lYM)

#--- load target river list ----
listDir = "/tank/utsumi/data/TLSM/GRDC_Station"
TargetListName  = listDir + "/TargetStations.np.one.Aft1993.100000km2.filtered.3.csv"
f=open(TargetListName, "r")
lines = f.readlines()
f.close()
lrivnum   = []
for sline in lines[1:]:
  line           = sline.strip().split(",")
  rivnum         = int(line[1])
  lrivnum.append(rivnum)

#--- river basin loop -------
for rivnum in lrivnum:
#for rivnum in [7]:
  a2mask  = ma.masked_not_equal(a2rivnum, rivnum)
  dprcp   = {}
  dqtot   = {}

  coef = 60.*60.*24.
  for itag in range(ntag):
    rivara       = ma.masked_where(a2mask.mask, a2lndara).sum()
    dprcp[itag]  = ma.masked_where(a2mask.mask, a3PRCP[itag]*a2lndara).sum()/rivara * coef
    dqtot[itag]  = ma.masked_where(a2mask.mask, a3QTOT[itag]*a2lndara).sum()/rivara * coef

  if vartype=="FRC":
    prcpall = array([dprcp[itag] for itag in range(ntag)]).sum()
    qtotall = array([dqtot[itag] for itag in range(ntag)]).sum()
    for itag in range(ntag):
      dprcp[itag] = dprcp[itag]/prcpall
      dqtot[itag] = dqtot[itag]/qtotall
  #****************
  #-- figure ------
  figplot  = plt.figure(figsize= (2,3))
  axplot   = figplot.add_axes([0.2, 0.1, 0.7, 0.8])

  #-- color ----
  dcolor   = {"tc":"r", "c":"royalblue","fbc":"lime","ms":"orange","ot":"gray"}
  #-- plot -----
  x1 = 1.0
  x2 = 2.0
  wbar = 0.8

  btmprcp = 0.0
  btmqtot = 0.0
  for itag in range(ntag):
    tag  = ltag[itag]
    axplot.bar(x1, dprcp[itag], bottom=btmprcp, width=wbar, color=dcolor[tag])
    axplot.bar(x2, dqtot[itag], bottom=btmqtot, width=wbar, color=dcolor[tag])

    btmprcp = btmprcp + dprcp[itag]
    btmqtot = btmqtot + dqtot[itag]
  #-- save ----- 
  rootDir  = "/tank/utsumi/out/TLSM"
  figDir   = rootDir + "/%s.%s.%02dc/fig"%(prj,run,ntag)
  util.mk_dir(figDir)
  figname  = figDir + "/bar.%s.%04d.png"%(vartype,rivnum)
  figplot.savefig(figname) 
  print figname


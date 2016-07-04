from numpy import *
import myfunc.util as util
import ConstH08
import H08
from collections import deque
iYM  = [1990,1]
eYM  = [2010,12]
#eYM  = [1990,12]
lYM  = util.ret_lYM(iYM, eYM)

PRJ = "JR55"
RUN = "____"
res = "one"
h08 = H08.H08(prj=PRJ, run=RUN, res=res)

#lsite = ["Datong","Bahadurabad","Vicksburg","StungTreng","Obidos"]
lsite = ["Obidos","Bahadurabad"]

dyx   = {
         "Obidos"      :[92,124]
        ,"Vicksburg"   :[56,88 ]
        ,"Datong"      :[60,296]
        ,"Bahadurabad" :[65,269]
        ,"StungTreng"  :[76,285]
        }

daxisdir = {"Obidos":"SN","Bahadurabad":"SN","Vicksburg":"SN"}

ntag   = 5
# see "/tank/utsumi/tag.mask/JRA55.nn.04c.one/TAGS.txt"
res     = "one"
ny,nx   = 180,360
Lat     = h08.Lat
Lon     = h08.Lon
uparaPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_ara_/rivara.GSWP2.one"
a2upara   = fromfile(uparaPath, float32).reshape(ny,nx)

lndaraPath= "/tank/utsumi/H08/H08_20130501/map/dat/lnd_ara_/lndara.GSWP2.one"
a2lndara  = fromfile(lndaraPath, float32).reshape(ny,nx)

numPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_num_/rivnum.GSWP2.one"
a2num   = fromfile(numPath, float32).reshape(ny,nx)

seqPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_seq_/rivseq.GSWP2.one"
a2seq   = fromfile(seqPath, float32).reshape(ny,nx)

dPrcpDir  = {"JR55": "/tank/utsumi/data/H08/ELSE.JRA55.L1_01u"}

H08Dir  = "/tank/utsumi/H08/H08_20130501"
orivDir ="%s/riv/out"%(H08Dir)
ptagDir ="/tank/utsumi/tag.mask/JRA55.nn.%04dc.one"%(ntag)

#******************************
def ret_lmean(a2in, axisdir):
  lout = deque([])
  if   axisdir =="SN":
    for iy in range(0,ny):
      lout.append(a2in[iy,:].mean())
  elif axisdir =="NS":
    for iy in range(ny-1,0-1,-1):
      lout.append(a2in[iy,:].mean())
  elif axisdir =="EW":
    for ix in range(0,nx):
      lout.append(a2in[:,ix].mean())
  elif axisdir =="WE":
    for ix in range(nx-1,0-1,-1):
      lout.append(a2in[:,ix].mean())

  return list(lout)

#******************************
def loadVar(Year,Mon, var):
  """
  var = PRCP, RIVOUT, QTOT
  """
  sDir  = "/tank/utsumi/H08/out/temp/TAG%s/05c/map"%(var)
  sPath = sDir + "/TAG%s.%s.%04d%02d.%s"%(var, PRJ, Year,Mon,res)
  return fromfile(sPath, float32).reshape(ntag, ny, nx)

#******************************
def ret_ltag(ntag):
  srcPath = "/tank/utsumi/tag.mask/JRA55.nn.%02dc.one/TAGS.txt"%(ntag)
  f=open(srcPath, "r")
  lines = f.readlines()
  f.close()
  return [s.strip() for s in lines]
#******************************
def ret_lseq(axisdir):
  if   axisdir == "SN":
    return list(Lat)
  elif axisdir == "NS":
    return list(Lat[::-1])
  elif axisdir == "WE":
    return list(Lon)
  elif axisdir == "EW":
    return list(Lon[::-1]) 
#******************************
a3PRCP   = zeros([ntag, ny, nx], float32)
a3RIVOUT = zeros([ntag, ny, nx], float32)
a3QTOT   = zeros([ntag, ny, nx], float32)
ltag     = ret_ltag(ntag)

for Year,Mon in lYM:
  a3PRCP   = a3PRCP +   loadVar(Year,Mon,"PRCP")
  a3RIVOUT = a3RIVOUT + loadVar(Year,Mon,"RIVOUT")
  a3QTOT   = a3QTOT   + loadVar(Year,Mon,"QTOT")

a3PRCP    = a3PRCP    / len(lYM)
a3RIVOUT  = a3RIVOUT  / len(lYM)
a3QTOT    = a3QTOT    / len(lYM)

#-- convert unit ------
for itag in range(ntag):
  #a3RIVOUT[itag] = a3RIVOUT[itag] / a2upara  # kg/s --> mm/s
  a3RIVOUT[itag] = a3RIVOUT[itag] / a2lndara  # kg/s --> mm/s

a3PRCP   = a3PRCP   * 60*60*24.
a3RIVOUT = a3RIVOUT * 60*60*24.
a3QTOT   = a3QTOT   * 60*60*24.

#----------------------
for site in lsite:
  iy,ix   = dyx[site]
  rivnum  = a2num[iy,ix]
  axisdir = daxisdir[site]
  lseq    = ret_lseq(axisdir)
  sout    = ""
  dlprcp  = {}
  dlqtot  = {}
  dlrivout= {}

  for itag in range(ntag):
    a2rivseq = ma.masked_where(a2num != rivnum, a2seq)

    seqmin   = a2rivseq.min()
    seqmax   = a2rivseq.max()
    dlprcp[itag]   = []
    dlrivout[itag] = [] 
    dlqtot[itag]   = [] 

    a2PRCP   = ma.masked_where(a2num != rivnum, a3PRCP[itag])
    a2RIVOUT = ma.masked_where(a2num != rivnum, a3RIVOUT[itag])
    a2QTOT   = ma.masked_where(a2num != rivnum, a3QTOT[itag])

    dlprcp[itag]   = ret_lmean(a2PRCP,   axisdir) 
    dlrivout[itag] = ret_lmean(a2RIVOUT, axisdir) 
    dlqtot[itag]   = ret_lmean(a2QTOT,   axisdir) 


  #---- write 1 ----------
  sout = "prcp&qtot&rivout\n"
  sout = sout + "," + ",".join(ltag) + ",,"+","+",".join(ltag) + ",,"+","+",".join(ltag)+ "\n"

  for iseq, seq in enumerate(lseq):
    sprcp  = "%d"%(iseq) + "," + ",".join(map(str, [dlprcp  [itag][iseq] for itag in range(ntag)]))
    sqtot  = "%d"%(iseq) + "," + ",".join(map(str, [dlqtot  [itag][iseq] for itag in range(ntag)]))
    srivout= "%d"%(iseq) + "," + ",".join(map(str, [dlrivout[itag][iseq] for itag in range(ntag)]))
    
    sout = sout + sprcp + "," + sqtot + "," + srivout + "\n"

  sDir = "/tank/utsumi/H08/out/temp/PROPAG/05c/csv"
  util.mk_dir(sDir)
  sPath= sDir + "/Axis.%s.%s.%s.1.csv"%(PRJ, site, axisdir)
  f=open(sPath,"w"); f.write(sout); f.close()
  print sPath 

  #---- write 2 ------------
  sout = "prcp&qtot&rivout\n"
  sout = sout + "," + ",".join(map(str,["%s-pr,%s-ro,%s-dis"%(tag,tag,tag) for tag in ltag])) + "\n"

  for iseq, seq in enumerate(lseq):
    sline  = ""
    for itag in range(ntag):
      sline  = sline + "," + ",".join(map( str, [dlprcp[itag][iseq], dlqtot[itag][iseq], dlrivout[itag][iseq]])) 

    sout   = sout + "%d"%(seq) + sline + "\n"

  sDir = "/tank/utsumi/H08/out/temp/PROPAG/05c/csv"
  util.mk_dir(sDir)
  sPath= sDir + "/Axis.%s.%s.%s.2.csv"%(PRJ, site, axisdir)
  f=open(sPath,"w"); f.write(sout); f.close()
  print sPath 
      




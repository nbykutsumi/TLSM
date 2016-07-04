from numpy import *
import myfunc.util as util
import ConstH08
iYM  = [1990,1]
eYM  = [2010,12]
lYM  = util.ret_lYM(iYM, eYM)

PRJ = "JR55"
RUN = "____"

lsite = ["Datong","Bahadurabad","Vicksburg","StungTreng","Obidos"]
#lsite = ["Datong"]

dyx   = {
         "Obidos"      :[92,124]
        ,"Vicksburg"   :[56,88 ]
        ,"Datong"      :[60,296]
        ,"Bahadurabad" :[65,269]
        ,"StungTreng"  :[76,285]
        }

ntag   = 5
# see "/tank/utsumi/tag.mask/JRA55.nn.04c.one/TAGS.txt"
res     = "one"
ny,nx   = 180,360

uparaPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_ara_/rivara.GSWP2.one"
a2upara   = fromfile(uparaPath, float32).reshape(ny,nx)

numPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_num_/rivnum.GSWP2.one"
a2num   = fromfile(numPath, float32).reshape(ny,nx)

seqPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_seq_/rivseq.GSWP2.one"
a2seq   = fromfile(seqPath, float32).reshape(ny,nx)

dPrcpDir  = {"JR55": "/tank/utsumi/data/H08/ELSE.JRA55.L1_01u"}

H08Dir  = "/tank/utsumi/H08/H08_20130501"
orivDir ="%s/riv/out"%(H08Dir)
ptagDir ="/tank/utsumi/tag.mask/JRA55.nn.%04dc.one"%(ntag)

#******************************
def loadPrcp(Year,Mon):
  sDir  = "/tank/utsumi/H08/out/temp/TAGPRCP/05c/map"
  sPath = sDir + "/TagPrcp.%s.%04d%02d.%s"%(PRJ, Year,Mon,res)
  a3dat = fromfile(sPath, float32).reshape(ntag, ny, nx)
  a3dat = a3dat * a2ara
  return a3dat

#******************************
def loadRivout(Year,Mon):
  sDir = "/tank/utsumi/H08/out/temp/TAGRIVOUT/05c/map"
  sPath= sDir + "/TagRivout.%s.%04d%02d.%s"%(PRJ, Year,Mon,res)
  return fromfile(sPath, float32).reshape(ntag, ny, nx)
#******************************
def ret_ltag(ntag):
  srcPath = "/tank/utsumi/tag.mask/JRA55.nn.%02dc.one/TAGS.txt"%(ntag)
  f=open(srcPath, "r")
  lines = f.readlines()
  f.close()
  return [s.strip() for s in lines]

#******************************
a3PRCP   = zeros([ntag, ny, nx], float32)
a3RIVOUT = zeros([ntag, ny, nx], float32)
ltag     = ret_ltag(ntag)

for Year,Mon in lYM:
  a3PRCP   = a3PRCP +   loadPrcp(Year,Mon)
  a3RIVOUT = a3RIVOUT + loadRivout(Year,Mon)

for site in lsite:
  iy,ix   = dyx[site]
  rivnum  = a2num[iy,ix]
  print site, rivnum
  sout    = ""
  dlprcp  = {}
  dlrivout= {}
  for itag in range(ntag):
    a2prcp   = ma.masked_where(a2num != rivnum, a3PRCP[itag])
    a2rivout = ma.masked_where(a2num != rivnum, a3RIVOUT[itag])
    a2rivseq = ma.masked_where(a2num != rivnum, a2seq)

    seqmin   = a2rivseq.min()
    seqmax   = a2rivseq.max()
    lseq     = arange(seqmin, seqmax+1, 2)
    dlprcp[itag]   = []
    dlrivout[itag] = [] 
    for seq in lseq:
      a2mask = ma.masked_outside(a2rivseq, seq, seq+1)
      prcp   = ma.masked_where(a2mask.mask, a2prcp).mean()
      rivout = ma.masked_where(a2mask.mask, a2rivout).mean()
      
      dlprcp[itag].append(prcp)
      dlrivout[itag].append(rivout)

  sout = "prcp&rivout\n"
  sout = sout + "," + ",".join(ltag) + ",,"+","+",".join(ltag) + "\n"

  for iseq, seq in enumerate(lseq):
    sprcp  = ",".join(map( str, [dlprcp  [itag][iseq] for itag in range(ntag)]))
    srivout= ",".join(map( str, [dlrivout[itag][iseq] for itag in range(ntag)]))
    
    sout   = sout + "%d,"%(seq) + sprcp + ",,%d,"%(seq) + srivout + "\n"

  #-- save ----
  sDir = "/tank/utsumi/H08/out/temp/PROPAG/05c/csv"
  util.mk_dir(sDir)
  sPath= sDir + "/PROPAG.%s.%s.csv"%(PRJ, site)
  f=open(sPath,"w"); f.write(sout); f.close()
  print sPath 
      




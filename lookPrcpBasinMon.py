from numpy import *
from datetime import datetime, timedelta
import myfunc.util as util
import ConstH08
import os, sys
import calendar

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

araPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_ara_/rivara.GSWP2.one"
a2ara   = fromfile(araPath, float32).reshape(ny,nx)

numPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_num_/rivnum.GSWP2.one"
a2num   = fromfile(numPath, float32).reshape(ny,nx)

seqPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_seq_/rivseq.GSWP2.one"
a2seq   = fromfile(seqPath, float32).reshape(ny,nx)

CH08    = ConstH08.ConstH08()
dPrcpDir  = {"JR55": "/tank/utsumi/data/H08/ELSE.JRA55.L1_01u"}

dMonName={1:"Jan",2:"Feb",3:"Mar",4 :"Apr",5 :"May",6 :"Jun"
         ,7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

#******************************
def ret_ltag(ntag):
  srcPath = "/tank/utsumi/tag.mask/JRA55.nn.%02dc.one/TAGS.txt"%(ntag)
  f=open(srcPath, "r")
  lines = f.readlines()
  f.close()
  return [s.strip() for s in lines]

#******************************

ltag   = ret_ltag(ntag)
da2upregion = {}
for site in lsite:
  iy,ix      = dyx[site]
  rivnum     = a2num[iy,ix]
  siteseq    = a2seq[iy,ix]
  a2upregion = ma.masked_where(a2num !=rivnum, a2seq)
  a2upregion = ma.masked_greater(a2upregion, siteseq)
  da2upregion[site] = a2upregion

dara = {}
for site in lsite:
  dara[site] = ma.masked_where(da2upregion[site].mask, a2ara).sum()

dlout = {}
for site in lsite:
  dlout[site] = []

for Year,Mon in lYM:
  nDay  = calendar.monthrange(Year,Mon)[1]
  sDir  = "/tank/utsumi/H08/out/temp/TAGPRCP/05c/map"
  sPath = sDir + "/TAGPRCP.%s.%04d%02d.%s"%(PRJ, Year,Mon,res)
  a3dat = fromfile(sPath, float32).reshape(ntag, ny, nx)
  a3dat = a3dat * a2ara
  for site in lsite:
    a2upregion  = da2upregion[site]
    ara         = dara[site]
    ltmp        = ["%s %04d"%(dMonName[Mon], Year)]
    for i in range(ntag):
      v   = ma.masked_where(a2upregion.mask, a3dat[i]).sum()/ara *60*60*24*nDay
      ltmp.append(v)

    dlout[site].append(ltmp) 
   
#-- save ---------
oDir  = "/tank/utsumi/H08/out/temp/TAGPRCP/%02dc/csv"%(ntag)
for site in lsite:
  ocsv  = util.list2csv(dlout[site])
  oPath = oDir + "/Monthly.%s.%s.csv"%(PRJ,site)
  f = open(oPath, "w"); f.write(ocsv); f.close()
  print oPath

 

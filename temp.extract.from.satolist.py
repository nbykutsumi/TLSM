from numpy import *

srcDir   = "/tank/utsumi/data/TLSM/GRDC_Station"
satolist = srcDir + "/GRDC.List.1deg.over10yr100000km2.Rank.csv"
grdclist = srcDir + "/Stations.np.one.csv"
olistname= srcDir + "/target.over10yr100000km2.csv"

lnoexist = [
3627030
,1897501
,1896502
,3627110
,5404270
,1891500
,3651807
,3649950
,5109151
,3629001
]

#--- load sato data -----
f=open(satolist, "r")
lines  = f.readlines()
f.close()

dsato = {}
for sline in lines[1:]:
  line = sline.strip().split(",")
  stnID = int(line[0])
  dsato[stnID]  =  line

#--- load grdc data ------
f=open(grdclist, "r")
lines  = f.readlines()
f.close()

dgrdc = {}
for sline in lines[1:]:
  line = sline.strip().split(",")
  stnID = int(line[5])
  dgrdc[stnID]  =  sline

#--- make out ------------
sout = lines[0]
for stnID in dsato.keys():
  if stnID in lnoexist:
    continue
  sout = sout + dgrdc[stnID]

sout = sout.strip()
f    = open(olistname, "w")
f.write(sout)
print olistname

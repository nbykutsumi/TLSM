iDir  = "/tank/utsumi/data/TLSM/GRDC_Station"

#--- load no exist data ---
noexistName = iDir + "/noexist.csv"
f     = open(noexistName, "r")
lines = f.readlines()
f.close()

lnoexist = []
for sline in lines:
  stnID = int(sline.strip())
  lnoexist.append(stnID) 

#--- filter ----
iPath = iDir + "/TargetStations.np.one.Aft1993.100000km2.csv"
f      = open(iPath, "r")
lines  = f.readlines()
f.close()

sout  = lines[0]
for sline in lines[1:]:
  line   = sline.split(",")
  stnID  = int(line[5])
  if stnID in lnoexist:
    continue
  else:
    sout = sout + sline

#--- write -----
oPath = iPath[:-4] + ".filtered.1.csv"
f     = open(oPath, "w")
f.write(sout)
f.close()
print oPath

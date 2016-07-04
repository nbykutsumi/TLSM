from numpy import *
import UtilTLSM

crd   = "np"
res   = "one"
ny,nx = 180,360
araPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_ara_/rivara.GSWP2.one"
a2ara   = fromfile(araPath, float32).reshape(ny,nx)
a2ara   = a2ara/1.e+6   # km^2

numPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_num_/rivnum.GSWP2.one"
a2num   = fromfile(numPath, float32).reshape(ny,nx)

#lsite = ["Obidos","Vicksburg","Thebes","Orsova","Datong","Bahadurabad","StungTreng"]
lsite = ["Obidos","Vicksburg","Datong","Bahadurabad","StungTreng"]

listDir  = "/tank/utsumi/data/TLSM/GRDC_Station"
GRDClist = listDir + "/20151127_GRDC_Stations_custom.csv"
oName    = listDir + "/Stations.%s.%s.csv"%(crd,res)
#-- load GRDC list -----------
f=open(GRDClist, "r")
lines = f.readlines()
f.close()
sout = "rivnum,Ypy,Xpy,AreaModel[km2],difArea[%]" + "," + lines[0] 

for sline in lines[1:]:
  line    = sline.strip().split(",")
  lat     = float(line[3])
  lon     = float(line[4])
  AreaGRDC= float(line[5])
  grdcid  = int(line[0])
  lyx     = UtilTLSM.latlon2yx([[lat,lon]], crd=crd, res=res)
  y,x     = lyx[0]
  #if grdcid !=3629000: # Obidos
  #  continue


  #-- check UpArea ---
  ymodel, xmodel = y, x
  difAreaMin     = 1.0e+20
  for dy,dx in [[dy,dx] for dy in [-1,0,1] for dx in [-1,0,1]]:
    Y,X     = y+dy, x+dx
    difArea = abs(a2ara[Y,X]/ AreaGRDC -1.0) *100.0
    #difArea = a2ara[Y,X] / AreaGRDC 
    if difArea < difAreaMin:
      difAreaMin     = difArea
      ymodel, xmodel = Y, X
      AreaModel      = a2ara[ymodel, xmodel]
      rivnum         = int(a2num[ymodel, xmodel])
    #print a2num[Y,X],"dy=",dy,"dx=",dx,"  ",Y,X,"**","%.2f"%(a2ara[Y,X]/1.e+6),"  ","%.1f"%(difArea),"[%]"
  #--------------------
  print lon,lat,xmodel, ymodel
  soline = "%s,%s,%s,%s,%s"%(rivnum,ymodel, xmodel, AreaModel, "%.2f"%(difAreaMin)) +"," + sline
  sout   = sout + soline 

#---- write to file ----
f = open(oName, "w"); f.write(sout); f.close()
print oName



from numpy import *
import UtilTLSM

ny,nx = 180,360
araPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_ara_/rivara.GSWP2.one"
a2ara   = fromfile(araPath, float32).reshape(ny,nx)

numPath = "/tank/utsumi/H08/H08_20130501/map/out/riv_num_/rivnum.GSWP2.one"
a2num   = fromfile(numPath, float32).reshape(ny,nx)

#lsite = ["Obidos","Vicksburg","Thebes","Orsova","Datong","Bahadurabad","StungTreng"]
lsite = ["Obidos","Vicksburg","Datong","Bahadurabad","StungTreng"]

dsiteinfo = {
 "Obidos":      [[-1.94,-55.51],   4680000. ]  # Obidos-Porto, Amazon
,"Vicksburg":   [[32.315,-90.906], 2964255. ]  # Vicksburg, MS, Mississippi
,"Datong":      [[30.77,117.62],   1705383  ] # Datong, Yangtze (Chang jiang)
,"Bahadurabad": [[25.18, 89.67],   636130   ] # Bahadurabad, Brahmaputra
,"StungTreng":  [[13.53, 105.95],  635000   ] # Stung Treng, Mekong
,"Thebes":      [[37.2167,-89.464],1847188  ] # Thebes, IL, Mississippi
,"Orsova":      [[44.7,22.42],     576232.  ]# Orsova, Donube
}

for site in lsite:
  latlon, Area = dsiteinfo[site]
  lyx =  UtilTLSM.latlon2yx(latlon)
  print "-"*50
  print site,"   ", "Area_obs=",Area
  for y,x in lyx:
    for dy,dx in [[dy,dx] for dy in [-1,0,1] for dx in [-1,0,1]]:
      Y,X = y+dy, x+dx
      difArea = (a2ara[Y,X]/1.e+6 - Area) / Area * 100.0
      print a2num[Y,X],"dy=",dy,"dx=",dx,"  ",Y,X,"**","%.2f"%(a2ara[Y,X]/1.e+6),"  ","%.1f"%(difArea),"[%]"

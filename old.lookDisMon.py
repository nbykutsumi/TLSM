from numpy import *
import myfunc.util as util

iYM    = [1990,1]
eYM    = [2010,12]
#eYM    = [2001,1]
lYM    = util.ret_lYM(iYM,eYM)
#PRJ="JR55"
#PRJ="GPCP"
#PRJ="GSMP"
#lPRJ = ["JR55","GPCP","GSMP"]
lPRJ = ["JR55"]
RUN="____"
"""
Obidos, Amazon
Thebes, IL, Mississippi
"""
lSite = ["Datong","Bahadurabad","Vicksburg","StungTreng","Obidos"]
ntag = 5
coef = 1.0  # mm/m^2 --> mm/m^2

dMonName={1:"Jan",2:"Feb",3:"Mar",4 :"Apr",5 :"May",6 :"Jun"
         ,7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

def load_csv(iPath):
  f = open(iPath, "r")
  lines =[map(float, line.strip().split(",")) for line in  f.readlines()]
  return array(lines, float32)  
#  return lines

for PRJ in lPRJ:
  for Site in lSite:
    baseDir = "/tank/utsumi/H08/out/TAGFLW/%02dc"%(ntag)
    if type(Site)==int:
      sDir    = baseDir + "/%04d"%(Site)
    else:
      sDir    = baseDir + "/%s"%(Site)
  
    lout = []
    for Year,Mon in lYM:
      iPath = sDir + "/%s%s%04d%02d.csv"%(PRJ,RUN,Year,Mon)
      a2in  = load_csv(iPath)
      #line  = [a2in[:,itag].sum() for itag in range(ntag+1)]
      #lout.append(line)
      #line  = ["%04d-%s"%(Year,dMonName[Mon])]
      line  = ["%s %04d"%(dMonName[Mon], Year)]
      #line  = line+[a2in[:,itag].mean()*coef for itag in range(ntag+1)][1:]
      line  = line+[a2in[:,itag].sum()*coef for itag in range(ntag+1)][1:]
      lout.append(line)
    ##- add date ---
    #adate = array(lYM)
    #aout  = hstack([adate, array(lout)])
    #- save ---
    ocsv  = util.list2csv(lout)
    #ocsv  = util.array2csv(aout)
    if type(Site)==int:
      oPath = sDir + "/Monthly.%s%s.%04d.csv"%(PRJ,RUN,Site)
    else:
      oPath = sDir + "/Monthly.%s%s.%s.csv"%(PRJ,RUN,Site)
    f=open(oPath,"w"); f.write(ocsv); f.close()
    print oPath

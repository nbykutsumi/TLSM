from datetime import datetime, timedelta
from math import floor, fmod
import ConstH08
import os

CH08  = ConstH08.ConstH08()
def ret_ltag(ntag=5, model="JRA55", wnflag="nn", res="one"):
  dirTaglist  = CH08.path_TagH08(DTime=datetime(1900,1,1), model=model, wnflag="nn", nclass=ntag, res=res)[0]
  pathTaglist = dirTaglist + "/TAGS.txt"

  f    = open(pathTaglist, "r")
  ltag = [s.strip() for s in f.readlines()]
  f.close()
  return ltag

def mk_dir(sdir):
  try:
    os.makedirs(sdir)
  except OSError:
    pass

def ret_lDTime(iDTime,eDTime,dDTime):
  total_steps = int( (eDTime - iDTime).total_seconds() / dDTime.total_seconds() + 1 )
  return [iDTime + dDTime*i for i in range(total_steps)]

def sa2np_3D(a):
  return roll(a[:,::-1,:], shape(a)[2]/2, axis=2)

def latlon2yx(llLatLon=False, crd="np",res="one"):
  """
  llLatLon: e.g. [[36,140],[-10,350]]
  """
  def func_np_one(lLatLon):
    Lat, Lon = lLatLon 
    x  = int(floor(fmod(Lon+180, 360)))
    y  = int(floor(90-Lat))
    return [y,x]

  if type(llLatLon[0]) not in [list, tuple]:
    llLatLon = [llLatLon]

  if (crd=="np")&(res=="one"):
    return map(func_np_one, llLatLon)
  

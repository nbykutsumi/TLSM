from numpy import *
import sys

class H08(object):
  def __init__(self, prj="GSW2",run="LR__",res="one"):
    self.prj=prj
    self.run=run
    self.res=res
    if res=="one":
      self.ny=180
      self.nx=360
      self.Lat    = arange(89.5, -89.5-0.01,-1.0)
      self.Lon    = arange(-179.5, 179.5+0.01, 1.0)
  def load_H08const(self, var, miss=-9999.):
    ny, nx    = self.ny, self.nx
    rootDir   = "/tank/utsumi/H08/H08_20130501/map"

    if var   == "riv_ara_":
      srcPath = rootDir + "/out/riv_ara_/rivara.GSWP2.one"
      a2var   = fromfile(srcPath, float32).reshape(ny,nx)
      a2var   = ma.masked_greater(a2var, 1e+18)
      a2var   = a2var/1.e+6   # km^2    
      a2var   = a2var.filled(miss)

    elif var == "lnd_ara_":
      srcPath = rootDir + "/dat/lnd_ara_/lndara.GSWP2.one"
      a2var   = fromfile(srcPath, float32).reshape(ny,nx)
      a2var   = ma.masked_greater(a2var, 1e+18)
      #a2var   = a2var / 1.e+6  # m^2 --> km^2
      a2var   = a2var.filled(miss)

    elif var == "riv_num_":
      srcPath = rootDir + "/out/riv_num_/rivnum.GSWP2.one"
      a2var   = fromfile(srcPath, float32).reshape(ny,nx).astype(int32)

    return a2var


  def load_H08var(self, var, DTime,tstp="DY"):
    if tstp == "DY":
      stime = "%04d%02d%02d"%(DTime.year,DTime.month,DTime.day)

    if var in [\
      "AvgSurfT"\
     ,"Evap____"\
     ,"FrcSWE__"\
     ,"FrcSoilM"\
     ,"LWdownou"\
     ,"LWnet___"\
     ,"PotEvap_"\
     ,"Qf______"\
     ,"Qg______"\
     ,"Qh______"\
     ,"Qle_____"\
     ,"Qs______"\
     ,"Qsb_____"\
     ,"Qtot____"\
     ,"Qv______"\
     ,"Rainfout"\
     ,"SAlbedo_"\
     ,"SWE_____"\
     ,"SWnet___"\
     ,"Snowfout"\
     ,"SoilMois"\
     ,"SoilTemp"\
     ,"SubSnow_"\
     ,"Tairout_"\
     ]:
      expr = "lnd"
    elif var in [\
      "riv_out_"\
     ,"riv_sto_"\
     ]:
      expr = "riv"
    else:
      print "check var=",var
      sys.exit()
    #srcDir  = "/data3/utsumi/H08/H08_20130501/%s/out/%s"%(expr,var)
    srcDir  = "/tank/utsumi/H08/H08_20130501/%s/out/%s"%(expr,var)
    srcPath = srcDir + "/%s%s%s.%s"%(self.prj,self.run,stime,self.res)
    if var in ["FrcSWE__","FrcSoilM"]:
      return fromfile(srcPath, float32).reshape(-1,self.ny,self.nx)
    else:
      return fromfile(srcPath, float32).reshape(self.ny,self.nx)

  def ret_pathTagVarMon(self, var, ntag, Year, Mon):
    stime   = "%04d%02d"%(Year,Mon)
    rootDir = "/tank/utsumi/out/H08/Mon/map"
    #----
    if var in ["PRCP"]:
      srcDir  = rootDir + "/%s.%s.%02dc/Tag.%s"%(self.prj,"Fcng",ntag,var)
    else:
      srcDir  = rootDir + "/%s.%s.%02dc/Tag.%s"%(self.prj,self.run,ntag,var)
    #----
    srcPath = srcDir + "/%s.%s"%(stime,self.res)
    return rootDir, srcDir, srcPath

  def loadTagVarMon(self, var, ntag, Year, Mon):
    rootDir, srcDir, srcPath = self.ret_pathTagVarMon(var, ntag, Year,Mon)
    return fromfile(srcPath, float32).reshape(ntag, self.ny, self.nx)



import os

class ConstH08(object):
  def __init__(self):
    pass

  def path_TagH08(self, DTime, model="JRA55",wnflag="nn",nclass=4,res="one",tstep="day"):
    if tstep == "day":
      stime = "%04d%02d%02d"%(DTime.year, DTime.month, DTime.day)
    if tstep == "6hr":
      print "check tres!!"
      sys.exit()

    tagDir  = "/tank/utsumi/tag.mask/%s.%s.%02dc.%s"%(model,wnflag,nclass,res)
    tagPath = tagDir + "/tag_%s.%s"%(stime, res)
    return tagDir, tagPath


  def ret_rivnumBBox(self):
    dBBox = {}
    dBBox = {
             1:[[-40,-80],[10,-30]]
            ,3:[[25,-120],[55,-70]]
            ,4:[[-40,-70],[0,-30]]
            ,7:[[40,80],[80,120]]
            ,8:[[40,100],[80,150]]
            ,10:[[30,100],[65,150]]
            ,11:[[20,85],[40,130]]
            ,12:[[45,-140],[75,-100]]
            ,16:[[35,-100],[60,-60]]
            ,25:[[50,-170],[75,-125]]
            ,26:[[35,5],[60,35]]
            ,27:[[5,90],[40,110]]
            ,32:[[30,-130],[60,-105]]
            ,34:[[55,140],[75,170]]
            ,45:[[10,100],[30,120]]
            ,50:[[60,90],[80,120]]
            ,58:[[55,45],[75,70]]
            ,99:[[-90,-180],[90,180]]
            }
    return dBBox

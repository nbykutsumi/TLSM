import subprocess
import os

iDir   = os.path.abspath(".")
oDir   = "/home/utsumi/Backup/%s"%(iDir.split("/")[-1])

try:
  os.mkdir(oDir)
except OSError:
  pass

cmd = ["rsync", "-uavr", "--delete"\
       ,"%s/"%(iDir), "%s/"%(oDir)]

subprocess.call(cmd)
print cmd


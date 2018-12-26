# this is going to be a simple test of importing yaml data into python and display in console

import yaml
import os, sys

with open("programtest.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

    try:
        print cfg["Programtest"]["Seq1"]["Duration"]
    except:
        print "Problem"


#for section in cfg:
 #   print(section)
#print(cfg['Seq1'])
#print(cfg['Seq2'])


#for filename in os.listdir(currentPath):
#            print filename
#            if(filename.endswith(".yaml")):
#                with open(os.path.join(currentPath, filename)) as myFile:
#                    results = yaml.load(myFile)
#                    try:
#                        print results["Programtest"]["Seq1"]["Duration"]
#                    except:
#                        print "Problem"

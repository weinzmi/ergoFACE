# this is going to be a simple test of importing yaml data into python and display in console

import yaml

with open("programtest.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

for section in cfg:
    print(section)
print(cfg['Seq1'])
print(cfg['Seq2'])

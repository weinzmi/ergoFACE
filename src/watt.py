import os
import sys
import yaml
import time

# ########################
# Watt program list and selection
# ########################

# TBD change to automatic directory detection
dirName = 'C:\\Users\\weikami\\Documents\\GitHub\\ergoFACE\\src\\wattprogram\\'
items = os.listdir(dirName)

fileList = []

for names in items:
    if names.endswith(".yaml"):
        fileList.append(names)

cnt = 0
for fileName in fileList:
    sys.stdout.write( "[%d] %s\n\r" %(cnt, fileName) )
    cnt = cnt + 1


fileName = int(input("\n\rSelect watt program [0 - " + str(cnt - 1) + "]: "))
print(fileList[fileName])

# ########################
# Watt Program execution
# ########################


f = open(dirName + fileList[fileName])
program = yaml.safe_load(f)
f.close()

for program_id in program['Prog']:
    duration = program['Prog'][program_id]['Duration']
    watt = program['Prog'][program_id]['Watt']
    print(watt," Watt will be applied for ",duration,"seconds")
    time.sleep(duration)

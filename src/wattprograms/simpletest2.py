import os
import sys
import yaml
import time

# ########################
# Watt program list and selection
# ########################

# TBD change to automatic directory detection
items = os.listdir("/home/pi/ergoFACE/src/wattprograms")

fileList = []

for names in items:
    if names.endswith(".yaml"):
        fileList.append(names)

cnt = 0
for fileName in fileList:
    sys.stdout.write( "[%d] %s\n\r" %(cnt, fileName) )
    cnt = cnt + 1


fileName = int(raw_input("\n\rSelect log file [0 - " + str(cnt - 1) + "]: "))
print(fileList[fileName])

# ########################
# Watt Program execution
# ########################


f = open(fileList[fileName])
program = yaml.safe_load(f)
f.close()

for program_id in program['Programtest']:
    # change the structure in yaml to avail program names "programtest"
    duration = program['Programtest'][program_id]['Duration'] 
    watt = program['Programtest'][program_id]['Watt'] 
    print watt," Watt will be applied for ",duration,"seconds"
    time.sleep(duration)
    

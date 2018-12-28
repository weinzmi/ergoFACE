import os
import sys
import yaml
import time


class Load:
    def __init__(self):

        # ########################
        # Watt program list and selection
        # ########################

        # TBD change to automatic directory detection
        global fileName
        global fileList
        global dirName

        self.dirName = 'C:\\Users\\weikami\\Documents\\GitHub\\ergoFACE\\src\\wattprogram\\'
        self.items = os.listdir(self.dirName)

        self.fileList = []

        for self.names in self.items:
            if self.names.endswith(".yaml"):
                self.fileList.append(self.names)

        cnt = 0

        for self.fileName in self.fileList:
            sys.stdout.write("[%d] %s\n\r" % (cnt, self.fileName))
            cnt = cnt + 1

        self.fileName = int(input("\n\rSelect watt program [0 - " + str(cnt - 1) + "]: "))
        print(self.fileList[self.fileName])

    def load_program(self):


        self.f = open(self.dirName + self.fileList[self.fileName])
        self.program = yaml.safe_load(self.f)
        self.f.close()

        for self.program_id in self.program['Prog']:
            self.duration = self.program['Prog'][self.program_id]['Duration']
            self.watt = self.program['Prog'][self.program_id]['Watt']
            print(self.watt, " Watt will be applied for ", self.duration, "seconds")
            time.sleep(self.duration)

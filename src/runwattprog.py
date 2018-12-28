import time
import yaml
from loadwattprog import module_load
import loadwattprog


def module_run():
    f = open(module_load().dirName + module_load().fileList[module_load().fileName])
    program = yaml.safe_load(f)
    f.close()
    for program_id in program['Prog']:
        duration = program['Prog'][program_id]['Duration']
        watt = program['Prog'][program_id]['Watt']
        print(watt, " Watt will be applied for ", duration, "seconds")
        time.sleep(duration)


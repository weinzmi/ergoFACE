import time
import loadwattprog


def run_watt_prog():
    for program_id in load_watt_prog.program['Prog']:
        duration = load_watt_prog.program['Prog'][program_id]['Duration']
        watt = load_watt_prog.program['Prog'][program_id]['Watt']
        print(watt, " Watt will be applied for ", duration, "seconds")
        time.sleep(duration)
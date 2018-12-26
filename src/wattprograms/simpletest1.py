import yaml, time

f = open("programtest.yaml")
program = yaml.safe_load(f)
f.close()

for program_id in program['Programtest']:
    duration = program['Programtest'][program_id]['Duration'] 
    watt = program['Programtest'][program_id]['Watt'] 
    print watt
    time.sleep(duration)
    

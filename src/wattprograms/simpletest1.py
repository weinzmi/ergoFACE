import yaml, time

f = open("programtest.yaml")
program = yaml.safe_load(f)
f.close()

for program_id in program['Programtest']:
    duration = program[program_id]['Duration'] 
    watt = program[program_id]['Watt'] 
    print watt," Watt will be applied for ",duration,"seconds"
    time.sleep(duration)
    

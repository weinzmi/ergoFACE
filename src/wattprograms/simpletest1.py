import yaml

f = open("programtest.yaml")
program = yaml.safe_load(f)
f.close()

for program_id in program['Programtest']:
    sequence = program['Programtest'][program_id]['Watt'] 
    print sequence

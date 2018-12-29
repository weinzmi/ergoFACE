def get_bool(prompt):
    while True:
        try:
           return {"true":True,"false":False}[input(prompt).lower()]
        except KeyError:
           print ("Invalid input please enter True or False!")

print (get_bool("Is Jonny Hungry?"))
import watt

# instantiate a class instance here
training = watt.Load()

# simulate the initiation and completition of 3 run thoughs of traingin program
# initialization only once
# append the program 3 times
for x in range(0, 3):
    training.load_program()
    print("We're on time %d" % (x))
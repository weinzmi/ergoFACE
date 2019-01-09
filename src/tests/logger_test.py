import csv
import time
# this is the header, written in text in the first row of CSV
CSVHEADER = ['TIME', 'POWER', 'CADENCE']

# ...


def processing_loop(csvfile):
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(CSVHEADER)

    # ...
    while True:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        power = 150
        cadence = 88

        csv_writer.writerow([timestr, power, cadence])
        csvfile.flush()
        time.sleep(5)


with open('results.csv', 'w') as csvfile:
    processing_loop(csvfile)

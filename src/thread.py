import ble_advertise
import ble_gatt_server
import rs232
import threading
from prettytable import PrettyTable
import time


def main():

    def task1():
        advertise = ble_advertise.main()
        advertise()

    def task2():
        server = ble_gatt_server.main()
        server()

    def task3():
        interface = rs232.main()
        interface()

    def task4():
        while True:
            t = PrettyTable(['Output', 'rs232'])
            t.add_row(['Power', rs232.Power])
            t.add_row(['Cadence', rs232.Cadence])
            t.add_row(['Speed', rs232.Speed])
            print(t)
            time.sleep(1)

    t1 = threading.Thread(target=task1)
    t2 = threading.Thread(target=task2)
    t3 = threading.Thread(target=task3)
    t4 = threading.Thread(target=task4)

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    # t1.join()
    # t2.join()
    # t3.join()


if __name__ == '__main__':
    main()

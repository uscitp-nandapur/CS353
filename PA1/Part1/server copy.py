import argparse
import socket
import select
import sys
from thread import *
import threading


print_lock = threading.Lock()


# thread fuction
def spawn_thread(c, d, ca):
    while True:

        # data received from client
        d, ca = c.recvfrom(1024)
        if (d):
            print " Data received from client : ", str(d)
            print " Sending data back to client : ", d.upper()
            c.sendto(d.upper(), ca)


        # lock released on exit
        print_lock.release()
        break

        # connection closed
    c.close()








def Main():
    parser = argparse.ArgumentParser(conflict_handler= "resolve")
    parser.add_argument("-p","--portno" , type=int,
                        help="supply a port number to connect to")
    parser.add_argument("-l","--logfile",
                        help="supply a file to write logs to")
    parser.add_argument("-h","--handler" , type=int,
                        help="supply a handler")
    args=parser.parse_args()

    port=args.portno
    logfile=args.logfile
    handler=args.handler

    address = 'localhost'

    f= open(logfile,"w+")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        # Create a socket object
    s.bind((address, port)) # Bind to the port
    f.write("server started on " + address + " at port " + str(port) + '\n')



    try:
        #print_lock.acquire()
        data, client_address = s.recvfrom(1024)
        s.sendto("welcome " + str(data).split(" ")[1], client_address)
        f.write("client connection from host " + address + " port " + str(port) + '\n')

        # define variables
        ads = str(client_address).split(", ")[0]
        lads = len(ads) - 1

        # print and write to logfile
        print str(data).split(" ")[1], "Registered from host", ads[2:lads], "port", port
        f.write("received register " + str(data).split(" ")[1] + " from host " + ads[2:lads] + " port " + str(port) + '\n')

        while True:

            #start_new_thread(spawn_thread, (s,))

            #Part1
            data, client_address = s.recvfrom(1024)
            if (data):
               print " Data received from client : ", str(data)
               print " Sending data back to client : ", data.upper()
               s.sendto(data.upper(), client_address)
    except:
        print('\n')
        f.write("terminating server..." + '\n')
    finally:
        f.close()
        s.close()

if __name__ == '__main__':
    Main()
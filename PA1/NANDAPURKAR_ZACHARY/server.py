import argparse
import socket
import select
import sys
from thread import *
import threading
import subprocess

print_lock = threading.Lock()

user_map = {

}

def route_message(sender, receiver, message, fi, handler):


    if handler == 1:
        print sender + " sending to " + receiver
        new_sock = user_map[receiver][0]
        new_message = "recvfrom " + sender + " " + message
        ca = user_map[receiver][1]
        fi.write("recvfrom " + sender + " to" + " " + receiver + " " + message + '\n')
        new_sock.sendto(new_message, ca)
    else:
        if receiver not in user_map:
            print receiver + " not registered with the server."
        else:
            new_sock = user_map[receiver][0]
            new_message = "recvfrom " + sender + " " + message
            ca = user_map[receiver][1]
            fi.write("recvfrom " + sender + " to" + " " + receiver + " " + message + '\n')
            new_sock.sendto(new_message, ca)







# thread fuction
def spawn_thread(c, d, ca, file,handler):
    # data received from client

    # vars
    port = ca[1]
    name = str(d).split(" ")[1]

    file.write("client connection from host " + str(ca[0]) + " port " + str(port) + '\n')

    # define variables
    ads = str(ca).split(", ")[0]
    lads = len(ads) - 1

    #print and write to logfile
    print str(d).split(" ")[1], "Registered from host", ads[2:lads], "port", port
    file.write(
       "received register " + str(d).split(" ")[1] + " from host " + ads[2:lads] + " port " + str(port) + '\n')

    while True:
        #print str(d).split(" ")[1] + " inside loop"
        d, ca = c.recvfrom(1024)

        if str(d).split(" ")[1] not in user_map:
            print str(d).split(" ")[1] + " not registered with server, spawning " + str(d).split(" ")[1]
            nlgf = "spawned_" + str(d).split(" ")[1] + ".txt"
            subprocess.call(["python", "client.py", "-s", "localhost", "-p", "12345", "-l", nlgf, "-n", str(d).split(" ")[1]])

       #print str(d).split(" ")[1] + " past server receive"
        if (str(d).split(" ")[0] == "sendto"):
            id = str(d).split(" ")[1]
            message = str(d).split(" ")[2:]
            file.write(str(d).split(" ")[0] + " " + id + " from " + name + " " + ' '.join(message) + '\n')
            route_message(name, id, ' '.join(message), file, handler)
            #c.sendto(''.join(message), ca)



def Main():
    parser = argparse.ArgumentParser(conflict_handler="resolve")
    parser.add_argument("-p", "--portno", type=int,
                        help="supply a port number to connect to")
    parser.add_argument("-l", "--logfile",
                        help="supply a file to write logs to")
    parser.add_argument("-h", "--handler", type=int,
                        help="supply a handler")
    args = parser.parse_args()

    port = args.portno
    logfile = args.logfile
    handler = args.handler

    address = 'localhost'

    f = open(logfile, "w+")

    # start the server
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a socket object
    s.bind((address, port))  # Bind to the port
    f.write("server started on " + address + " at port " + str(port) + '\n')
    f.flush()

    try:

        #problem is here!!
        count = 0
        while (True):
            count += 1
            data, client_address = s.recvfrom(1024)
            tempsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            tempsocket.bind((address, port + count))  # Bind to the port

            # // after thread
            s.sendto(str(port + count), client_address)

            # send message back
            s.sendto("welcome " + str(data).split(" ")[1], client_address)

            username = str(data).split(" ")[1]
            user_map[username]=(tempsocket, client_address)


            #print_lock.acquire()
            t = threading.Thread(target=spawn_thread, name=(str(data).split(" ")[1]),
                                 args=(tempsocket, data, client_address, f, handler,))
            t.setDaemon(True)
            t.start()



    except:
        print('\n')
        f.write("terminating server..." + '\n')
    finally:
        t._Thread__stop()
        f.close()
        s.close()


if __name__ == '__main__':
    Main()
import argparse
import socket
import select
import sys
from thread import *
import threading
import subprocess
import os
import time

print_lock = threading.Lock()

user_map = {

}
tcp_sock_list = []

def route_message(sender, receiver, message, fi, handler, socks):
    if handler == 1:
        #spawn new user
        if receiver not in user_map:
            print receiver + " not registered with server, spawning " + receiver
            new_logfile = "spawned_" + receiver + ".txt"
            send_subp(new_logfile, receiver)
        #continue sending
        time.sleep(1)
        new_sock = user_map[receiver][0]
        new_message = "recvfrom " + sender + " " + message
        ca = user_map[receiver][1]
        fi.write("recvfrom " + sender + " to" + " " + receiver + " " + message + '\n')
        new_sock.sendto(new_message, ca)
    else:
        if receiver not in user_map:
            print receiver + " not registered with the server."
            send_TCP(socks, sender, receiver, message, handler)
        else:
            new_sock = user_map[receiver][0]
            new_message = "recvfrom " + sender + " " + message
            ca = user_map[receiver][1]
            fi.write("recvfrom " + sender + " to" + " " + receiver + " " + message + '\n')
            new_sock.sendto(new_message, ca)


def send_subp(logfile_, name_):
    proc = subprocess.Popen(
        ["python", "client.py", "-s", "localhost", "-p", "12345", "-l", logfile_, "-n", name_])


# thread fuction
def spawn_thread(c, d, ca, file,handler):
    # vars
    port = ca[1]
    name = str(d).split(" ")[1]

    file.write("client connection from host " + str(ca[0]) + " port " + str(port) + '\n')

    # define variables
    ads = str(ca).split(", ")[0]
    lads = len(ads) - 1
    shortened_hostname = ads[2:lads]

    #print and write to logfile
    print name, "Registered from host", shortened_hostname, "port", port
    file.write(
       "received register " + name + " from host " + shortened_hostname + " port " + str(port) + '\n')

    while True:
        d, ca = c.recvfrom(1024)
        if (str(d).split(" ")[0] == "sendto"):
            id = str(d).split(" ")[1]
            message = str(d).split(" ")[2:]
            file.write(str(d).split(" ")[0] + " " + id + " from " + name + " " + ' '.join(message) + '\n')
            route_message(name, id, ' '.join(message), file, handler, tcp_sock_list)


def send_TCP(socks, sender, receiver, message, handler):
    for sock in socks:
        print "in sendTCP for loop"
        print sock
        sock.send("recvfrom " + sender + " to " + receiver + " " + message)

def handle_TCP_outgoing(sock, handler,_file):
    # tcp connection (PA2)

    sock.listen(5)  # Now wait for client connection.
    print "hi"
    print " Ready to accept the connections ! !"
    connection, overlay_address = sock.accept()
    tcp_sock_list.append(connection)
    print "Accepted!"
    while True:
        data = connection.recv(1024)
        if (data):
            if (str(data).split(" ")[0] == "recvfrom"):
                print "received" + data
                sender = str(data).split(" ")[1]
                receiver = str(data).split(" ")[3]
                message = str(data).split(" ")[4:]
                #file.write(str(d).split(" ")[0] + " " + id + " from " + name + " " + ' '.join(message) + '\n')
                route_message(sender, receiver, ' '.join(message), _file, handler, tcp_sock_list)


def handle_TCP_incoming(sock, handler,_file):
    while True:
        data = sock.recv(1024)
        if (data):
            if (str(data).split(" ")[0] == "recvfrom"):
                print "received" + data
                sender = str(data).split(" ")[1]
                receiver = str(data).split(" ")[3]
                message = str(data).split(" ")[4:]
                # file.write(str(d).split(" ")[0] + " " + id + " from " + name + " " + ' '.join(message) + '\n')
                route_message(sender, receiver, ' '.join(message), _file, handler, tcp_sock_list)


def Main():
    parser = argparse.ArgumentParser(conflict_handler="resolve")
    parser.add_argument("-s", "--serveroverlayIP",
                        help="supply an ip address")
    parser.add_argument("-t", "--serveroverlay", type=int,
                        help="supply a port number to connect to")
    parser.add_argument("-o", "--overlayport", type=int,
                        help="supply a port number to connect to")
    parser.add_argument("-p", "--portno", type=int,
                        help="supply a port number to connect to")
    parser.add_argument("-l", "--logfile",
                        help="supply a file to write logs to")
    parser.add_argument("-h", "--handler", type=int,
                        help="supply a handler")
    args = parser.parse_args()

    #assign variables to ports
    if args.serveroverlayIP:
        serveroverlayIP = args.serveroverlayIP
    if args.serveroverlay:
        serveroverlay=args.serveroverlay
    overlayport=args.overlayport
    port = args.portno
    logfile = args.logfile
    handler = args.handler

    address = 'localhost'

    #create and open the logfile
    f = open(logfile, "w+")


    # start the UDP server
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a socket object
    s.bind((address, port))  # Bind to the port
    f.write("server started on " + address + " at port " + str(port) + '\n')
    f.flush()

    # start the listening TCP Server (PA2)
    o = socket.socket()  # Create a socket object
    o_port = overlayport  # Reserve a port for your service.
    o.bind((address, overlayport))  # Bind to the port
    print "Binding completed  ! !"

    #connect to the existing server
    p = socket.socket()




    if args.serveroverlayIP and args.serveroverlay:
        print "Connecting to server..."
        p.connect((serveroverlayIP, serveroverlay))
        print "Connected!"
        tcp_sock_list.append(p)
        k = threading.Thread(target=handle_TCP_incoming, args=(p, handler, f,))
        k.setDaemon(True)
        k.start()

    r = threading.Thread(target=handle_TCP_outgoing, args=(o, handler,f,))
    r.setDaemon(True)
    r.start()

    try:
        count = 0
        while (True):
            count += 1



            print "pre UDP"
            data, client_address = s.recvfrom(1024)
            tempsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            tempsocket.bind((address, port + count))  # Bind to the port

            print "Made it"
            # // after thread
            s.sendto(str(port + count), client_address)




            # send message back
            s.sendto("welcome " + str(data).split(" ")[1], client_address)

            #add elements to map
            username = str(data).split(" ")[1]
            user_map[username]=(tempsocket, client_address)

            #start thread
            t = threading.Thread(target=spawn_thread, name=(str(data).split(" ")[1]),
                                 args=(tempsocket, data, client_address, f, handler,))
            print str(data).split(" ")[1], client_address
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
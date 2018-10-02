import socket               # Import socket module
import time
import argparse
import threading

user_map = {

}



def handle_connection(c):
    while True:
        data = c.recv(1024)
        if (data):
            if (str(data).split(" ")[0] == "received"):
                trigger = str(data).split(" ")[0]
                user = str(data).split(" ")[2]
                user_map[user]=c
            else:
                if (str(data).split(" ")[1] not in user_map):
                    c.send("spawn " + str(data))
                else:
                    c.send("found " + str(data))





def Main():
    parser = argparse.ArgumentParser(conflict_handler="resolve")
    parser.add_argument("-port", "--port", type=int,
                        help="supply a port")
    parser.add_argument("-log", "--log",
                        help="supply a logfile to write to")
    args = parser.parse_args()

    # define variables
    port = args.port
    logfile = args.log

    f = open(logfile, "w+")
    # Create a socket object
    s = socket.socket()  # Reserve a port for your service.
    s.bind(('localhost', port))  # Bind to the port
    print " Binding completed  ! !"

    s.listen(5)  # Now wait for client connection.
    print " Ready to accept the connections ! !"

    try:
        while True:
            connection, client_address = s.accept()  # Establish connection with client.
            k = threading.Thread(target=handle_connection, args=(connection,))
            k.setDaemon(True)
            k.start()

    except:
        print " Something went wrong in accepting conenction "


if __name__ == '__main__':
    Main()
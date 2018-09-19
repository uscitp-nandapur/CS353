import socket  # Import socket module
import argparse
import sys
import threading

parser = argparse.ArgumentParser(conflict_handler="resolve")
parser.add_argument("-s", "--serverip",
                    help="supply an ip address for the server")
parser.add_argument("-p", "--portno", type=int,
                    help="supply a port number to connect to")
parser.add_argument("-l", "--logfile",
                    help="supply a file to write logs to")
parser.add_argument("-n", "--name",
                    help="supply a name")
args = parser.parse_args()

serverip = args.serverip
port = args.portno
logfile = args.logfile
name = args.name

f = open(logfile, "w+")



if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (serverip, port)
    f.write("connecting to server " + str(serverip) + " at port " + str(port) + '\n')


    def recv():
        while True:
            data = sock.recv(1024)
            if not data: sys.exit(0)
            print data
            f.write(data + '\n')

    try:
        sock.sendto("register " + name, server_address)
        f.write("sending register message " + name + '\n')


        # new port
        data, server_detail = sock.recvfrom(1024)
        server_address = (serverip, int(data))
        #print data

        # in the data, it says talke to em on 8001
        # because server_detail talk localhost, 8000

        data, server_detail = sock.recvfrom(1024)
        #print data

        print "connected to server and registered"
        f.write("received welcome" + '\n')

        input = True
        print "waiting for messages..."
        while (input):
            t=threading.Thread(target=recv)
            t.setDaemon(True)
            t.start()
            user_input = str(raw_input(''))
            f.write(user_input + '\n')
            if (user_input == 'exit'):
                input = False
                t._Thread__stop()
            else:
                sock.sendto(user_input, server_address)
                #data, server_detail = sock.recvfrom(1024)

    except:
        print "Something went wrong while connecting to server"
    finally:
        f.write("terminating client..." + '\n')
        f.close()
        sock.close()






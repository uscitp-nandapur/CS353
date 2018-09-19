import socket  # Import socket module
import argparse





parser = argparse.ArgumentParser(conflict_handler= "resolve")
parser.add_argument("-s","--serverip",
                    help="supply an ip address for the server")
parser.add_argument("-p","--portno" , type=int,
                    help="supply a port number to connect to")
parser.add_argument("-l","--logfile",
                    help="supply a file to write logs to")
parser.add_argument("-n","--name" ,
                    help="supply a name")
args=parser.parse_args()

serverip=args.serverip
port=args.portno
logfile=args.logfile
name=args.name

f= open(logfile,"w+")

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (serverip, port)
    f.write("connecting to server " + str(serverip) + " at port " + str(port) + '\n')



    try:
        sock.sendto("register " + name, server_address)
        f.write("sending register message " + name + '\n')
        data, server_detail = sock.recvfrom(1024)
        print"connected to server and registered"
        f.write("received welcome" + '\n')

        input = True
        print "waiting for messages..."
        while (input):
            user_input = str(raw_input(''))
            if(user_input=='exit'):
                input=False
            else:
                sock.sendto(user_input, server_address)
                data, server_detail = sock.recvfrom(1024)
                print " Received message from server : ", data

    except:
        print "Something went wrong while connecting to server"
    finally:
        f.write("terminating client..." + '\n')
        f.close()
        sock.close()






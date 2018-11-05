import argparse
import os
import select
import socket
import struct
import sys
import time

icmp_echo_req = 8

def median(_list):
    n = len(_list)
    if n < 1:
            return None
    if n % 2 == 1:
            return sorted(_list)[n//2]
    else:
            return sum(sorted(_list)[n//2-1:n//2+1])/2.0

#Structure from resource in PDF (pklaus)
def checksum(in_str, _file):

    total = 0
    midpt = (len(in_str) / 2) * 2
    count = 0
    _file.write("Entering Checksum Calc" + '\n')
    b_size=256

    #Get Stringlength
    string_len = len(in_str)

    while count < midpt:
        current = ord(in_str[count]) + ord(in_str[count + 1])*b_size
        total = total + current

        #If bitsize > 16
        total = total & 0xffffffff
        count = count + 2

    if midpt < string_len:
        total = total + ord(in_str[len(in_str) - 1])

        #If bitsize > 16
        total = total & 0xffffffff


    total = (total >> 16) + (total & 0xffff)
    total = total + (total >> 16)

    #NOT Total
    answer = ~total

    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    _file.write("Answer = " + str(answer) + '\n')
    return answer

def utf8len(s):
    return len(s.encode('utf-8'))

# def init_checksum(pack_size):
#     _cs = 0
#     pheader = struct.pack("bbHHh", icmp_echo_req, 0, _checksum, id, 1)
#     size = struct.calcsize("d")
#     data = (pack_size - bytes) * 'Q'
#     data = struct.pack("d", time.time()) + data
#     _checksum = checksum(pheader + data)

def incoming_ping(my_socket, id, timeout, _f):
    remaining = timeout
    while True:
        #Get time now
        starttime = time.time()

        _f.write("Start time was" + str(starttime) + '\n')

        time_rd = select.select([my_socket], [], [], remaining)
        time_pending = (time.time() - starttime)
        if time_rd[0] == []:
            return 0

        _received = time.time()
        received_packet, addr = my_socket.recvfrom(1024)

        _f.write("Received at " + str(_received) + '\n')

        #IP Portion
        ipHeader = received_packet[:20]

        Version, TypeOfSvc, Length, ID, Flags, ipTTL, \
        Protocol, Checksum, SrcIP, DestIP = struct.unpack(
            "!BBHHHBBHII", ipHeader)

        #ICMP Portion
        icmpHeader = received_packet[20:28]
        type, code, checksum, packet_id, sequence = struct.unpack(
            "bbHHh", icmpHeader
        )
        if packet_id == id:
            bytes = struct.calcsize("d")
            time_sent = struct.unpack("d", received_packet[28:28 + bytes])[0]
            elapsed = _received - time_sent
            return elapsed, ipTTL
        remaining = remaining - time_pending
        if remaining <= 0:
            return "Error"

def send_a_ping(dest_addr, timeout, pack_size, _f):

    #Get protocol: ICMP Being used
    icmp = socket.getprotobyname("icmp")
    try:
        mysock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error, (errno, msg):
        if errno == 1:
            raise socket.error(msg)
        raise

    #Bitwise AND Current Process ID
    my_id = os.getpid() & 0xFFFF

    dest = socket.gethostbyname(dest_addr)
    nh_size = pack_size - 8

    _checksum = 0
    pheader = struct.pack("bbHHh", icmp_echo_req, 0, _checksum, my_id, 1)
    size = struct.calcsize("d")

    #Allocate Space for Payload
    data = 256 * "Q"

    data = struct.pack("d", time.time()) + data
    _checksum = checksum(pheader + data, _f)
    nheader = struct.pack(
        "bbHHh", icmp_echo_req, 0, socket.htons(_checksum), my_id, 1
    )
    packet = nheader + data

    # RAW Socket requires port field, Add dummy port to port field
    mysock.sendto(packet, (dest, 23))


    delay, TTL = incoming_ping(mysock, my_id, timeout, _f)

    mysock.close()
    return delay, TTL

def display_delay_statistics(delay_array,count):
    total=0
    for delay in delay_array:
        total=total+delay

    min_delay=min(delay_array)
    max_delay=max(delay_array)
    med=median(delay_array)
    return min_delay, max_delay, med



def multi_ping(dest_addr, timeout, count, psize, _f):
    delays = []
    icount = 0
    for i in xrange(count):
        print "reply from " + dest_addr + ":",
        _f.write("Receiving Reply")
        try:
            transit_time, TTL  =  send_a_ping(dest_addr, timeout, psize, _f)
        except socket.gaierror, e:
            print "failed"
            break

        if transit_time  ==  None:
            print "failed. (timeout within %ssec.)" % timeout
        else:
            #seconds to milliseconds conversion
            transit_time  =  transit_time * 1000
            delays.append(transit_time)
            icount=icount+1
            print "icmp_seq=" + str(i) + " bytes=" + str(psize) + " " + "time=%.2fms" % transit_time + " TTL=" + str(TTL)
            _f.write("icmp_seq=" + str(i) + " bytes=" + str(psize) + " " + "time=%.2fms" % transit_time + " TTL=" + str(TTL) + '\n')
    print "Ping Statistics for " + dest_addr + ":"
    percentage = ((count-icount)/count)*100
    print "Packets:" + "Sent: " + str(count) + " Received: " + str(icount) + " Lost: " + str(count-icount) \
          + "(" + str(percentage) + '%' + " loss" ")"
    min_d, max_d, avg_d = display_delay_statistics(delays,count)
    print "Minimum= %.2fms" % min_d + " " + "Maximum= %.2fms" % max_d + " " + "Average= %.2fms" % avg_d


def Main():
    parser = argparse.ArgumentParser(conflict_handler="resolve")
    parser.add_argument("-p", "--payload",
                        help="supply a port number to connect to")
    parser.add_argument("-c", "--count", type=int,
                        help="supply a file to write logs to")
    parser.add_argument("-d", "--IP",
                        help="supply a destination")
    parser.add_argument("-l", "--logfile",
                        help="supply a logfile")
    args = parser.parse_args()

    payload = args.payload
    count = args.count
    dest=args.IP
    logfile = args.logfile

    timeout=2

    f=open(logfile, "w+")
    bytes=utf8len(payload)
    print "Pinging " + dest + " " "with " + str(bytes) + " bytes of data " + payload + ":"
    multi_ping(dest, timeout, count, bytes, f)


if __name__ == '__main__':
    Main()
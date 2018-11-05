import argparse
import os
import select
import socket
import struct
import sys
import time

icmp_echo_req = 8

#structure from resource in PDF (pklaus)
def checksum(in_str):

    total = 0
    midpt = (len(in_str) / 2) * 2
    count = 0

    b_size=256
    while count < midpt:
        current = ord(in_str[count + 1])*b_size+ord(in_str[count])
        total = total + current
        total = total & 0xffffffff
        count = count + 2
    if midpt < len(in_str):
        total = total + ord(in_str[len(in_str) - 1])
        total = total & 0xffffffff
    total = (total >> 16) + (total & 0xffff)
    total = total + (total >> 16)
    answer = ~total
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def utf8len(s):
    return len(s.encode('utf-8'))

# def init_checksum(pack_size):
#     _checksum = 0
#     pheader = struct.pack("bbHHh", icmp_echo_req, 0, _checksum, id, 1)
#     size = struct.calcsize("d")
#     data = (pack_size - bytes) * 'Q'
#     data = struct.pack("d", time.time()) + data
#     _checksum = checksum(pheader + data)

def incoming_ping(my_socket, id, timeout):
    time_left = timeout
    while True:
        #Get time now
        starttime = time.time()


        what_ready = select.select([my_socket], [], [], time_left)
        how_long_in_select = (time.time() - starttime)
        if what_ready[0] == []:
            return

        time_received = time.time()
        received_packet, addr = my_socket.recvfrom(1024)

        #IP Portion
        ipHeader = received_packet[:20]

        ipVersion, ipTypeOfSvc, ipLength, ipID, ipFlags, ipTTL, \
        ipProtocol, ipChecksum, ipSrcIP, ipDestIP = struct.unpack(
            "!BBHHHBBHII", ipHeader)

        #ICMP Portion
        icmpHeader = received_packet[20:28]
        type, code, checksum, packet_id, sequence = struct.unpack(
            "bbHHh", icmpHeader
        )
        if packet_id == id:
            bytes = struct.calcsize("d")
            time_sent = struct.unpack("d", received_packet[28:28 + bytes])[0]
            return (time_received - time_sent), ipTTL

        time_left = time_left - how_long_in_select
        if time_left <= 0:
            return

def send_a_ping(dest_addr, timeout, pack_size):

    #Get protocol: ICMP Being used
    icmp = socket.getprotobyname("icmp")
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
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
    data = 256 * "Q"
    data = struct.pack("d", time.time()) + data
    _checksum = checksum(pheader + data)
    nheader = struct.pack(
        "bbHHh", icmp_echo_req, 0, socket.htons(_checksum), my_id, 1
    )
    packet = nheader + data

    # RAW Socket requires port field, Add dummy port to port field
    my_socket.sendto(packet, (dest, 23))


    delay, TTL = incoming_ping(my_socket, my_id, timeout)

    my_socket.close()
    return delay, TTL

def display_delay_statistics(delay_array,count):
    total=0
    for delay in delay_array:
        total=total+delay

    min_delay=min(delay_array)
    max_delay=max(delay_array)
    med=median(delay_array)
    return min_delay, max_delay, med

def median(lst):
    n = len(lst)
    if n < 1:
            return None
    if n % 2 == 1:
            return sorted(lst)[n//2]
    else:
            return sum(sorted(lst)[n//2-1:n//2+1])/2.0

def multi_ping(dest_addr, timeout, count, psize):
    delays = []
    icount = 0
    for i in xrange(count):
        print "reply from " + dest_addr + ":",
        try:
            delay, TTL  =  send_a_ping(dest_addr, timeout, psize)
        except socket.gaierror, e:
            print "failed"
            break

        if delay  ==  None:
            print "failed. (timeout within %ssec.)" % timeout
        else:
            #seconds to milliseconds conversion
            delay  =  delay * 1000
            delays.append(delay)
            icount=icount+1
            print "icmp_seq=" + str(i) + " bytes=" + str(psize) + " " + "time=%.2fms" % delay + " TTL=" + str(TTL)
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

    bytes=utf8len(payload)
    print "Pinging " + dest + " " "with " + str(bytes) + " bytes of data " + payload + ":"
    multi_ping(dest, 2, count, bytes)


if __name__ == '__main__':
    Main()
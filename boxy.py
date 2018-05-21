import getopt
import os
import sys

import hooker

from relay import status, tcp, udp

hooker.EVENTS.append(["boxy.start", "boxy.stop"])

import extensions.file_logger

RELAYPORT = 0
REMOTEPORT = 0
REMOTEADDRESS = ""
RECVBUFF = 2048
PROTOCOL = "UDP"
SSL = False
CERT = None
KEY = None

HELP = """
Invalid arguments, usage:
    boxy.py -i <input port> -p <remote port> -a <remote address> [-t|-s -c <cert-file> -k <key-file>]
    To create a self signed certificate:
        openssl req -x509 -nodes -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365
"""


def stop():
    print("Quitting...")

    if PROTOCOL == "UDP":
        udp.stop()
    else:
        tcp.stop()

    hooker.EVENTS["boxy.stop"]()
    os._exit(0)


# Process args
try:
    OPTIONS, ARGS = getopt.getopt(sys.argv[1:], "b:c:k:i:p:a:ts")
except getopt.GetoptError:
    print(HELP)
    sys.exit(2)

try:
    for option, arg in OPTIONS:
        if option == "-i":
            RELAYPORT = int(arg)
        elif option == "-p":
            REMOTEPORT = int(arg)
        elif option == "-a":
            REMOTEADDRESS = arg
        elif option == "-t":
            PROTOCOL = "TCP"
        elif option == "-s":
            PROTOCOL = "TCP"
            SSL = True
        elif option == "-c":
            CERT = arg
        elif option == "-k":
            KEY = arg
        elif option == "-b":
            RECVBUFF = int(arg)
except ValueError:
    print(HELP)
    sys.exit(2)

if not (0 < RELAYPORT <= 65535 and 0 < REMOTEPORT <= 65535 and REMOTEADDRESS != ""):
    print(HELP)
    sys.exit(2)

if SSL and not (CERT and KEY):
    print(HELP)
    sys.exit(2)

print("Relay starting on port {0}, relaying {1} to {2}:{3}"
      .format(RELAYPORT, PROTOCOL, REMOTEADDRESS, REMOTEPORT))

hooker.EVENTS["boxy.start"](RELAYPORT, REMOTEADDRESS, REMOTEPORT, PROTOCOL, SSL, CERT, KEY)

if PROTOCOL == "UDP":
    udp.start(RELAYPORT, REMOTEADDRESS, REMOTEPORT, RECVBUFF)
else:
    tcp.start(RELAYPORT, REMOTEADDRESS, REMOTEPORT, RECVBUFF, SSL, CERT, KEY)

status.start(RELAYPORT, REMOTEADDRESS, REMOTEPORT)

try:
    try:
        while raw_input() != "quit":
            continue
    except NameError:
        # Python 3
        while input() != "quit":
            continue

    stop()
except KeyboardInterrupt:
    stop()
except EOFError:
    # This exception is raised when ctrl-c is used to close
    # the application on Windows, appears to be thrown twice?
    try:
        stop()
    except KeyboardInterrupt:
        os._exit(0)

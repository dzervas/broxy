import socket
import threading
import sys
import getopt
import os
from relay import status, tcp, udp

RELAYPORT = 0
REMOTEPORT = 0
REMOTEADDRESS = ""
PROTOCOL = "UDP"

HELP = """Invalid arguments, usage:
    boxy.py -i <input port> -p <remote port> -a <remote address> [-t]"""


def bquit():
    print("Quitting...")

    if PROTOCOL == "UDP":
        udp.stop()
    else:
        tcp.stop()

    os._exit(0)


# Process args
try:
    OPTIONS, ARGS = getopt.getopt(sys.argv[1:], "i:p:a:t")
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
except ValueError:
    print(HELP)
    sys.exit(2)

if not (0 < RELAYPORT <= 65535 and 0 < REMOTEPORT <= 65535 and REMOTEADDRESS != ""):
    print(HELP)
    sys.exit(2)

print("Relay starting on port {0}, relaying {1} to {2}:{3}"
      .format(RELAYPORT, PROTOCOL, REMOTEADDRESS, REMOTEPORT))

if PROTOCOL == "UDP":
    udp.start(RELAYPORT, REMOTEADDRESS, REMOTEPORT)
else:
    tcp.start(RELAYPORT, REMOTEADDRESS, REMOTEPORT)

status.start(RELAYPORT, REMOTEADDRESS, REMOTEPORT)

try:
    try:
        while raw_input() != "quit":
            continue
    except NameError:
        # Python 3
        while input() != "quit":
            continue

    bquit()
except KeyboardInterrupt:
    bquit()
except EOFError:
    # This exception is raised when ctrl-c is used to close
    # the application on Windows, appears to be thrown twice?
    try:
        bquit()
    except KeyboardInterrupt:
        os._exit(0)

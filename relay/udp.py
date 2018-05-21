import sys
import socket
import threading
from relay import status

_KILL = False
_RELAYPORT = 0
_REMOTEADDRESS = ""
_REMOTEPORT = 0


def relay():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", _RELAYPORT))

    incomingsetup = False
    clientport = 0
    clientip = ""

    while True:
        data, fromaddr = sock.recvfrom(1024)

        if _KILL:
            sock.close()
            return

        if not incomingsetup:
            clientport = fromaddr[1]
            clientip = fromaddr[0]
            incomingsetup = True

        if fromaddr[0] == clientip:
            # Forward from client to server
            sock.sendto(data, (_REMOTEADDRESS, _REMOTEPORT))
            status.BYTESTOREMOTE += sys.getsizeof(data)
        else:
            # Forward from server to client
            sock.sendto(data, (clientip, clientport))
            status.BYTESFROMREMOTE += sys.getsizeof(data)


def start(relayport, remoteaddress, remoteport):
    global _RELAYPORT
    global _REMOTEADDRESS
    global _REMOTEPORT

    _RELAYPORT = relayport
    _REMOTEADDRESS = remoteaddress
    _REMOTEPORT = remoteport

    relaythread = threading.Thread(target=relay)
    relaythread.start()


def stop():
    _KILL = True

    # Send anything to the input port to trigger it to read, therefore allowing the thread to close
    quitsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    quitsock.sendto("killing", ("127.0.0.1", _RELAYPORT))
    quitsock.close()

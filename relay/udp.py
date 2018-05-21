import logging
import socket
import sys
import threading

import hooker

from relay import status

hooker.EVENTS.append([
    "udp.start",
    "udp.pre_recv",
    "udp.post_recv",
    "udp.pre_c2s",
    "udp.post_c2s",
    "udp.pre_s2c",
    "udp.post_s2c",
    "udp.stop"
])

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

    hooker.EVENTS["udp.start"]()

    while True:
        hooker.EVENTS["udp.pre_recv"](sock)
        data, fromaddr = sock.recvfrom(1024)
        hooker.EVENTS["udp.pre_recv"](sock, data, fromaddr)

        if _KILL:
            hooker.EVENTS["udp.stop"](sock)
            sock.close()

            return

        if not incomingsetup:
            clientport = fromaddr[1]
            clientip = fromaddr[0]
            incomingsetup = True

        if fromaddr[0] == clientip and fromaddr[1] == clientport:
            # Forward from client to server
            hooker.EVENTS["udp.pre_c2s"](data)
            sock.sendto(data, (_REMOTEADDRESS, _REMOTEPORT))
            hooker.EVENTS["udp.post_c2s"](data)
            status.BYTESTOREMOTE += sys.getsizeof(data)
        else:
            # Forward from server to client
            hooker.EVENTS["udp.pre_s2c"](data)
            sock.sendto(data, (clientip, clientport))
            hooker.EVENTS["udp.post_s2c"](data)
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

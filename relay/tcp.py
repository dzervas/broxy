import sys
import socket
import threading

import hooker

from relay import status

hooker.EVENTS.append([
    "tcp.start",
    "tcp.accept",
    "tcp.pre_c2s",
    "tcp.post_c2s",
    "tcp.pre_s2c",
    "tcp.post_s2c",
    "tcp.stop"
])

_KILL = False
_RELAYPORT = 0
_REMOTEADDRESS = ""
_REMOTEPORT = 0

_CLIENTS = 0
_SERVERS = 0

_SOCKS = []


def acceptclients():
    global _SOCKS

    clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsock.bind(("0.0.0.0", _RELAYPORT))
    clientsock.listen(10)

    hooker.EVENTS["tcp.start"]()

    while True:
        clientconn, _ = clientsock.accept()

        if _KILL:
            hooker.EVENTS["tcp.stop"](sock)
            clientsock.close()
            for sock in _SOCKS:
                sock.close()
            return

        serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversock.connect((_REMOTEADDRESS, _REMOTEPORT))
        hooker.EVENTS["tcp.accept"](clientsock, serversock)

        _SOCKS.append(clientconn)
        _SOCKS.append(serversock)

        clientthread = threading.Thread(target=client, kwargs={
            'clnt': clientconn,
            'srv': serversock
        })
        clientthread.start()

        serverthread = threading.Thread(target=server, kwargs={
            'clnt': clientconn,
            'srv': serversock
        })
        serverthread.start()


def close(clnt, srv):
    try:
        clnt.close()
    except socket.error:
        pass

    try:
        srv.close()
    except socket.error:
        pass


def client(clnt, srv):
    global _CLIENTS
    _CLIENTS += 1
    while True:
        try:
            data = clnt.recv(1)

            if not data:
                close(clnt, srv)
                break

            hooker.EVENTS["tcp.pre_c2s"](data, clnt, srv)
            srv.sendall(data)
            hooker.EVENTS["tcp.post_c2s"](data, clnt, srv)
            status.BYTESTOREMOTE += sys.getsizeof(data)
        except socket.error:
            close(clnt, srv)
            break
    _CLIENTS -= 1


def server(clnt, srv):
    global _SERVERS
    _SERVERS += 1
    while True:
        try:
            data = srv.recv(1)

            if data == "":
                close(clnt, srv)
                break

            hooker.EVENTS["tcp.pre_s2c"](data, clnt, srv)
            clnt.sendall(data)
            hooker.EVENTS["tcp.post_s2c"](data, clnt, srv)
            status.BYTESFROMREMOTE += sys.getsizeof(data)
        except socket.error:
            close(clnt, srv)
            break
    _SERVERS -= 1


def start(relayport, remoteaddress, remoteport):
    global _RELAYPORT
    global _REMOTEADDRESS
    global _REMOTEPORT

    _RELAYPORT = relayport
    _REMOTEADDRESS = remoteaddress
    _REMOTEPORT = remoteport

    acceptthread = threading.Thread(target=acceptclients)
    acceptthread.start()


def stop():
    global _KILL
    _KILL = True
    # Connect to the input port therefore allowing the thread to close
    quitsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    quitsock.connect(("127.0.0.1", _RELAYPORT))
    quitsock.close()

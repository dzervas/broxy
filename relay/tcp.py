import sys
import socket
import threading
from relay import status

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

    while True:
        clientconn, _ = clientsock.accept()

        if _KILL:
            clientsock.close()
            for sock in _SOCKS:
                sock.close()
            return

        serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversock.connect((_REMOTEADDRESS, _REMOTEPORT))

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

            if data == "":
                close(clnt, srv)
                break

            srv.sendall(data)
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

            clnt.sendall(data)
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

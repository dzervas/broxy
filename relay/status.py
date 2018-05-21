import sys
import time
import os
import threading

BYTESTOREMOTE = 0
BYTESFROMREMOTE = 0

_RELAYPORT = 0
_REMOTEADDRESS = ""
_REMOTEPORT = 0


def reportbandwidth():
    global BYTESTOREMOTE
    global BYTESFROMREMOTE

    step = 0

    while True:
        time.sleep(1)

        if sys.platform == "win32":
            os.system('cls')
        else:
            os.system('clear')

        print("Relaying on port {0} to {1}:{2}"
              .format(_RELAYPORT, _REMOTEADDRESS, _REMOTEPORT))
        print("From remote: {0:.6f}MB/s | To remote: {1:.6f}MB/s"
              .format(float(BYTESFROMREMOTE)/1000000, float(BYTESTOREMOTE)/1000000))

        if step == 0:
            print("\\")
            step += 1
        elif step == 1:
            print("|")
            step += 1
        elif step == 2:
            print("/")
            step += 1
        elif step == 3:
            print("-")
            step = 0

        BYTESFROMREMOTE = 0
        BYTESTOREMOTE = 0


def start(relayport, remoteaddress, remoteport):
    global _RELAYPORT
    global _REMOTEADDRESS
    global _REMOTEPORT

    reportbandwidththread = threading.Thread(target=reportbandwidth)
    reportbandwidththread.daemon = True
    reportbandwidththread.start()

    _RELAYPORT = relayport
    _REMOTEADDRESS = remoteaddress
    _REMOTEPORT = remoteport

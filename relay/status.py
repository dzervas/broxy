from __future__ import print_function
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
        time.sleep(0.5)

        if sys.platform == "win32":
            os.system('cls')

        if step == 0:
            loading = "\\"
            step += 1
        elif step == 1:
            loading = "|"
            step += 1
        elif step == 2:
            loading = "/"
            step += 1
        elif step == 3:
            loading = "-"
            step = 0

        print("Relaying on port {0} to {1}:{2} | From remote: {3:.6f}MB/s | To remote: {4:.6f}MB/s... {5} ".format(_RELAYPORT, _REMOTEADDRESS, _REMOTEPORT, float(BYTESFROMREMOTE)/1000000, float(BYTESTOREMOTE)/1000000, loading), end="\r")
        sys.stdout.flush()

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

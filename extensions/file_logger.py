import logging
from hooker import hook

logging.basicConfig(filename='broxy.log', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())


@hook("broxy.start")
def start(lport, rhost, rport, protocol, ssl, cert, key):
    sslstr = ""
    if ssl:
        protocol = "SSL"
        sslstr += " using cert: %s and key: %s" % (cert, key)
    logging.info("Started %s%s relay localhost:%d <-> %s:%d" % (protocol, sslstr, lport, rhost, rport))


@hook("tcp.pre_c2s")
def tc2s(data, client, server):
    caddr = client.getsockname()
    saddr = server.getsockname()
    logging.info("%s:%d->%s:%d %s%s" % (caddr[0], caddr[1], saddr[0], saddr[1], data.strip(), " " * 100))


@hook("tcp.pre_s2c")
def ts2c(data, client, server):
    caddr = client.getsockname()
    saddr = server.getsockname()
    logging.info("%s:%d<-%s:%d %s%s" % (caddr[0], caddr[1], saddr[0], saddr[1], data.strip(), " " * 100))


@hook("udp.pre_c2s")
def uc2s(data):
    logging.info("CLIENT %s%s\r" % (data.strip(), " " * 100))


@hook("udp.pre_s2c")
def us2c(data):
    logging.info("SERVER %s%s\r" % (data.strip(), " " * 100))


@hook("broxy.stop")
def stop():
    logging.info("Quitting...")

import logging
from hooker import hook

logging.basicConfig(filename='boxy.log', level=logging.DEBUG)


@hook("boxy.start")
def start(lport, rhost, rport):
    logging.info("Started relay localhost:%d <-> %s:%d" % (lport, rhost, rport))


@hook("tcp.pre_c2s")
def tc2s(data, client, server):
    caddr = client.getsockname()
    saddr = server.getsockname()
    logging.info("%s:%d->%s:%d %s" % (caddr[0], caddr[1], saddr[0], saddr[1], data.strip()))


@hook("tcp.pre_s2c")
def ts2c(data, client, server):
    caddr = client.getsockname()
    saddr = server.getsockname()
    logging.info("%s:%d<-%s:%d %s" % (caddr[0], caddr[1], saddr[0], saddr[1], data.strip()))


@hook("udp.pre_c2s")
def uc2s(data):
    logging.info("CLIENT %s" % data.strip())


@hook("udp.pre_s2c")
def us2c(data):
    logging.info("SERVER %s" % data.strip())


@hook("boxy.stop")
def stop():
    logging.info("Quitting...")

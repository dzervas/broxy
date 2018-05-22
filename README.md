broxy
====

Simple two-way UDP and TCP packet relay.
Fork of [boxy](https://github.com/OliverF/boxy) by OliverF. Thank you! <3

# Usage
`broxy.py -i <input port> -a <remote address> -p <remote port> [-t] [-s] [-c <cert>] [-k <key>]`

- **-i \<input port\>**: Input port the relay listens on (and relays back from)
- **-a \<remote address\>**: Remote IP address the relay will send incoming data to
- **-p \<remote port\>**: Remote port the relay will send incoming data to
- **-t**: Relay TCP (otherwise relay UDP if flag is not set)
- **-s**: Relay SSL over TCP
- **-c \<cert\>**: SSL certificate file (by default cert.pem)
- **-k \<key\>**: SSL private key file (by default key.pem)

# UDP example

**Relaying UDP data to remote server B at 192.0.2.1:1234, with the relay running at 192.0.2.0:4321**

1. Start the relay: `python broxy.py -i 4321 -a 192.0.2.1 -p 1234`

2. Connect to the relay at 192.0.2.0:4321

3. Done! You can send data to the relay and it will be relayed to the remote server, and you will receive the data returned from the remote server back from the relay itself

# TCP example

**Relaying TCP data to remote server B at 192.0.2.1:1234, with the relay running at 192.0.2.0:4321**

Same as the UDP example above, but to start the relay, add the -t flag:
`python broxy.py -i 4321 -a 192.0.2.1 -p 1234 -t`
Any new TCP connections to the relay will be automatically relayed to the remote server.

# SSL example

**Relaying SSL data to remote server B at 192.0.2.1:1234, with the relay running at 192.0.2.0:4321**

Same as the other examples, but to start the relay, add the -s flag:
`python broxy.py -i 4321 -a 192.0.2.1 -p 1234 -s`
Any new SSL connections to the relay will be automatically relayed to the remote server.

**Usefull OpenSSL commands:**
- Create self signed certificate: `openssl req -x509 -nodes -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365`
- SSL client: `openssl s_client -connect 192.0.2.1:4321`
- SSL server: `openssl s_server -cert scert.pem -key skey.pem -accept 1234`

NOTE: For a more real-life testing, use different keys for broxy and openssl server

#!/usr/bin/env python
# a simple TCP client
  
import socket
import string

BUFSIZE = 4096
TIMEOUT = 3
waveipfile = '/srv/labdata/Software/waveip'

remote = open(waveipfile,"r")
addr = remote.readline()
info = string.split(addr,':')
host = info[0]
port = int(info[1])

goodconnection = True
try:
    cmd ='WAVELENGTH'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)
    sock.sendto(cmd, (host, port))
    message = sock.recv(1024)
    sock.close()
except:
    goodconnection = False
    message = "<i>Cannot connect to Wavenet server, \
                please check if server functions properly \
                and refresh this page</i>"

print "Content-type: text\html\n\n"
print "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">"
print "<html><head>"

if (goodconnection):
    print "<meta http-equiv=\"refresh\" content=\"1\" >"

print "<title>WA-1500 wavemeter</title> \
        </head><body>"
print "<h1>%s</h1>" %(message)
print "</body></html>"

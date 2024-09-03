#!/usr/bin/python

if 1:
    import sys
    dpipe = open("/tmp/applet.log", "a", 1)
    sys.stdout = dpipe
    sys.stderr = dpipe
    print "starting"

from twisted.internet import gtk2reactor
gtk2reactor.install()

# System imports
import pygtk
pygtk.require("2.0")

import gtk, gnome.applet, gnome.ui

# Twisted imports
from twisted.internet import protocol, reactor
from twisted.protocols import basic

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8888

class Applet:
    def __init__(self, container):
        self.container = container
        self.setupWindow()

    def setupWindow(self):
        self.entry = gtk.Entry()
        self.entry.set_property('editable', gtk.FALSE)
        self.entry.set_size_request(250, 24)
        self.container.add(self.entry)
        self.container.show_all()

    def writeMessage(self, line):
        self.entry.set_text(line)

        
class ChatterClientProtocol(basic.LineReceiver):
    def connectionMade(self):
        self.factory.setProtocolInstance(self)
                       
    def lineReceived(self, line):
        self.factory.lineReceived(line)

class ChatterClientFactory(protocol.ReconnectingClientFactory):
    protocol = ChatterClientProtocol

    def __init__(self, chatter):
        self.protocolInstance = None
        self.chatter = chatter

    def setProtocolInstance(self, myProtocolInstance):
        self.protocolInstance = myProtocolInstance
    
    def lineReceived(self, line):
        self.chatter.writeMessage(line)

    def sendMessage(self, msg):
        self.protocolInstance.sendLine(msg)
        
    def disconnect(self):
        self.protocolInstance.transport.loseConnection()

def factory(container, iid):
    applet = Applet(container)
    container.show_all()
    reactor.connectTCP(DEFAULT_HOST, DEFAULT_PORT, ChatterClientFactory(applet))
    return gtk.TRUE

reactor.startRunning()
reactor.simulate()
gnome.applet.bonobo_factory("OAFIID:GNOME_ChatApplet_Factory", 
gnome.applet.Applet.__gtype__, 
                            "ChatApplet", "0", factory)

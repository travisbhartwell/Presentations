#!/usr/bin/python

from twisted.protocols import basic
from twisted.internet import protocol
from twisted.internet import reactor

class ChatterServerProtocol(basic.LineReceiver):
    def connectionMade(self):
        self.factory.protocols.append(self)
        
    def connectionLost(self, why):
        self.factory.protocols.remove(self)
        
    def lineReceived(self, line):
        self.factory.lineReceived(line)
    
class ChatterServerFactory(protocol.ServerFactory):
    protocol = ChatterServerProtocol
    
    def __init__(self):
        self.protocols = []
        
    def lineReceived(self, line):
        for protocol in self.protocols:
            protocol.sendLine(line)
            
reactor.listenTCP(8888, ChatterServerFactory())
reactor.run()

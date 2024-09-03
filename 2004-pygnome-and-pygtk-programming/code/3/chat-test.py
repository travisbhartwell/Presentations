#!/usr/bin/python

from twisted.internet import gtk2reactor
gtk2reactor.install()

import gtk, gtk.glade
from twisted.internet import protocol, reactor
from twisted.protocols import basic

class Chatter:
    def __init__(self):
        self.setupWindow()
        self.factory = None

    def setupWindow(self):
        self.xml = gtk.glade.XML('chat-3.glade', 'window')

        self.window = self.xml.get_widget('window')
        self.textView = self.xml.get_widget('textView')
        self.buffer = self.textView.get_buffer()

        self.entry = self.xml.get_widget('entry')
        
        self.statusBar = self.xml.get_widget('statusBar')
        self.statusContextID = self.statusBar.get_context_id('PyCon Chatter')

        self.connectItem = self.xml.get_widget('connectItem')
        self.disconnectItem = self.xml.get_widget('disconnectItem')
        
        ## signals = {
##         'close': self.close,
##         'sendMessage': self.sendMessage,
##         'clear': self.clear,
##         'connect': self.connect,
##         'disconnect': self.disconnect
##         }

        self.xml.signal_autoconnect(self)

        self.setDisconnected()
        
    def setDisconnected(self):
        self.connected = False
        self.disconnectItem.set_sensitive(gtk.FALSE)
        self.connectItem.set_sensitive(gtk.TRUE)
        self.statusBar.push(self.statusContextID, 'Disconnected')

    def setConnected(self):
        self.connected = True
        self.connectItem.set_sensitive(gtk.FALSE)
        self.disconnectItem.set_sensitive(gtk.TRUE)
        self.statusBar.push(self.statusContextID, 'Connected')
        
    def sendMessage(self, entry):
        if self.connected:
            self.factory.sendMessage("<%s>\t%s" % (self.username, self.entry.get_text()))
            self.entry.set_text('')
        else:
            error = gtk.MessageDialog(self.window,
                               gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                               gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                               "Please connect before sending messages")

            error.run()
            error.destroy()
    
    def writeMessage(self, msg):
        self.buffer.insert_at_cursor('%s\n' % msg)
        
    def close(self, widget):
        reactor.stop()

    def clear(self, widget):
        self.buffer.set_text('')

    def connect(self, widget):
        username, host, port = ConnectDialog().run()

        if username != None:
            self.username = username
            self.factory = ChatterClientFactory(self)
            reactor.connectTCP(host, port, self.factory)
            self.setConnected()

    def disconnect(self, widget):
        self.factory.disconnect()
        self.factory = None
        self.setDisconnected()

class ConnectDialog:
    DEFAULT_USERNAME = 'Chatter'
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 8888
    
    def __init__(self):
        self.setupDialog()

    def setupDialog(self):
        self.xml = gtk.glade.XML('chat-3.glade', 'connectDialog')

        self.dialog = self.xml.get_widget('connectDialog')
        self.usernameEntry = self.xml.get_widget('usernameEntry')
        self.hostEntry = self.xml.get_widget('hostEntry')
        self.portEntry = self.xml.get_widget('portEntry')

        self.usernameEntry.set_text(self.DEFAULT_USERNAME)
        self.usernameEntry.set_activates_default(gtk.TRUE)
        
        self.hostEntry.set_text(self.DEFAULT_HOST)
        self.hostEntry.set_activates_default(gtk.TRUE)
        
        self.portEntry.set_text(str(self.DEFAULT_PORT))
        self.portEntry.set_activates_default(gtk.TRUE)
        
    def run(self):
        self.dialog.show_all()

        result = self.dialog.run()

        if result == gtk.RESPONSE_OK:
            username = self.usernameEntry.get_text()
            host = self.hostEntry.get_text()
            port = int(self.portEntry.get_text())
        else:
            username = host = port = None

        self.dialog.destroy()
        
        return (username, host, port)
        
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

        
Chatter()
reactor.run()

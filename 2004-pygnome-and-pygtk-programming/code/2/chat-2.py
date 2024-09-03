#!/usr/bin/python

import gtk, gtk.glade

class Chatter:
    def __init__(self):
        self.setupWindow()

    def setupWindow(self):
        self.xml = gtk.glade.XML('chat-2.glade')

        self.textView = self.xml.get_widget('textView')
        self.buffer = self.textView.get_buffer()

        self.entry = self.xml.get_widget('entry')

        signals = {
        'close': self.close,
        'sendMessage': self.sendMessage,
        'clear': self.clear,
        }

        self.xml.signal_autoconnect(signals)

    def sendMessage(self, entry):
        self.buffer.insert_at_cursor('%s\n' % self.entry.get_text())
        self.entry.set_text('')

    def close(self, widget):
        gtk.mainquit()

    def clear(self, widget):
        self.buffer.set_text('')

Chatter()
gtk.main()

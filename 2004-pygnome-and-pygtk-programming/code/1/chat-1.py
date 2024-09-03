#!/usr/bin/python

import pygtk
pygtk.require("2.0")

import gtk

class Chatter:
    def __init__(self):
        self.setupWindow()

    def setupWindow(self):
        self.window = gtk.Window()
        self.window.set_title('PyCon Chatter')
        self.window.set_default_size(640, 480)

        accelGroup = gtk.AccelGroup()
        self.window.add_accel_group(accelGroup)
        
        vbox = gtk.VBox()
        self.window.add(vbox)

        menuBar = gtk.MenuBar()
        vbox.pack_start(menuBar, expand=gtk.FALSE)

        fileMenu = gtk.Menu()
        quitItem = gtk.ImageMenuItem(stock_id='gtk-quit')
        quitItem.connect("activate", self.close)
        quitItem.add_accelerator("activate", accelGroup, ord('Q'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        fileMenu.append(quitItem)
        fileItem = gtk.MenuItem("_File")
        fileItem.set_submenu(fileMenu)
        menuBar.append(fileItem)

        editMenu = gtk.Menu()
        clearItem = gtk.ImageMenuItem(stock_id='gtk-clear')
        clearItem.connect("activate", self.clear)
        editMenu.append(clearItem)
        editItem = gtk.MenuItem("_Edit")
        editItem.set_submenu(editMenu)
        menuBar.append(editItem)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.textView = gtk.TextView()
        self.buffer = self.textView.get_buffer()

        self.textView.set_editable(gtk.FALSE)
        self.textView.set_cursor_visible(gtk.FALSE)
        self.textView.set_wrap_mode(gtk.WRAP_WORD)

        sw.add(self.textView)
        vbox.pack_start(sw)

        self.entry = gtk.Entry()
        self.entry.connect("activate", self.sendMessage)
        vbox.pack_start(self.entry, expand=gtk.FALSE)

        self.window.set_focus(self.entry)
        self.window.show_all()

    def sendMessage(self, entry):
        self.buffer.insert_at_cursor('%s\n' % self.entry.get_text())
        self.entry.set_text('')

    def close(self, widget):
        gtk.mainquit()

    def clear(self, widget):
        self.buffer.set_text('')

    def about(self, widget):
        print "ABOUT"

Chatter()
gtk.main()

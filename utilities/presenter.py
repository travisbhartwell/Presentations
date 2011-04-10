#!/usr/bin/python

from twisted.internet import gtk2reactor
gtk2reactor.install()

import gtk
import poppler

from twisted.web.server import Site
from twisted.web.resource import Resource, NoResource
from twisted.internet import reactor

PRESENTATION_FILE = "file:///home/nafai/Downloads/presentation.pdf"


def generateCommandsPage():
    global commands

    commandsHTML = "<ul>" + \
    "".join( \
        ["<li><a href=\"/%s\">%s</a></li><br><br>" % (command, command) \
         for command in commands.keys()]) + \
    "</ul>"

    return "<html><body>%s</body></html>" % commandsHTML


class PresentationControlCommand(Resource):

    def __init__(self, fn):
        Resource.__init__(self)
        self.fn = fn

    def render_GET(self, _):
        self.fn()
        return generateCommandsPage()


class LinksCommand(Resource):

    def render_GET(self, _):
        return generateCommandsPage()


class PresentationControlDispatcher(Resource):

    def getChild(self, path, _):
        if path == '':
            return LinksCommand()
        elif path in commands:
            return PresentationControlCommand(commands[path])
        else:
            return NoResource()

commands = {}


class Presenter(object):

    def __init__(self):
        self.presentation = poppler.document_new_from_file(PRESENTATION_FILE,
                                                           None)
        self.n_pages = self.presentation.get_n_pages()
        self.current_page = self.presentation.get_page(0)

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.fullscreen()
        self.window.set_title("Presenter")
        self.window.connect("delete-event", gtk.main_quit)
        self.window.connect("window-state-event", self.on_state_changed)

        self.dwg = gtk.DrawingArea()
        self.dwg.connect("expose-event", self.on_expose)
        self.window.add(self.dwg)

        self.window.add_events(gtk.gdk.KEY_PRESS_MASK)
        self.window.connect("key-press-event", self.on_key_pressed)

        self.window.show_all()

    def display_previous(self):
        current_page_num = self.current_page.get_index()
        next_page_num = current_page_num - 1

        if next_page_num >= 0:
            self.current_page = self.presentation.get_page(next_page_num)
            self.dwg.queue_draw()

    def display_next(self):
        current_page_num = self.current_page.get_index()
        next_page_num = current_page_num + 1

        if next_page_num < self.n_pages:
            self.current_page = self.presentation.get_page(next_page_num)
            self.dwg.queue_draw()

    def on_key_pressed(self, _, event):
        if event.keyval in (gtk.gdk.keyval_from_name(key) for key in
                            ("space", "Return", "Right", "Page_Down")):
            self.display_next()
        elif event.keyval in (gtk.gdk.keyval_from_name(key) for key in
                              ("Left", "Page_Up")):
            self.display_previous()
        elif event.keyval == gtk.gdk.keyval_from_name("Escape"):
            self.quit()

    def change_scale(self):
        self.width, self.height = self.window.get_size()
        self.doc_width, self.doc_height = self.current_page.get_size()
        self.x_scale = float(self.width) / self.doc_width
        self.y_scale = float(self.height) / self.doc_height

    def on_state_changed(self, *_):
        self.change_scale()
        self.dwg.set_size_request(self.width, self.height)
        self.dwg.queue_draw()

    def on_expose(self, widget, _):
        self.change_scale()
        cr = widget.window.cairo_create()
        cr.set_source_rgb(1, 1, 1)

        cr.scale(self.x_scale, self.y_scale)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        self.current_page.render(cr)

    def quit(self):
        reactor.stop()

    def main(self):
        global commands

        commands = {"next": self.display_next,
                    "previous": self.display_previous,
                    "quit": self.quit}

        root = PresentationControlDispatcher()
        factory = Site(root)
        reactor.listenTCP(8888, factory)
        reactor.run()


if __name__ == "__main__":
    presenter = Presenter()
    presenter.main()

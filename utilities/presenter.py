#!/usr/bin/python

import gtk
import poppler

PRESENTATION_FILE = "file:///home/nafai/Downloads/presentation.pdf"

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

    def on_key_pressed(self, widget, event):
        if event.keyval == gtk.gdk.keyval_from_name("space"):
            current_page_num = self.current_page.get_index()
            next_page_num = current_page_num + 1

            if next_page_num < self.n_pages:
                self.current_page = self.presentation.get_page(next_page_num)
                self.dwg.queue_draw()

    def change_scale(self):
        self.width, self.height  = self.window.get_size()
        self.doc_width, self.doc_height = self.current_page.get_size()
        self.x_scale = float(self.width) / self.doc_width
        self.y_scale = float(self.height)/ self.doc_height


    def on_state_changed(self, widget, event):
        self.change_scale()
        self.dwg.set_size_request(self.width, self.height)
        self.dwg.queue_draw()


    def on_expose(self, widget, event):
        self.change_scale()
        cr = widget.window.cairo_create()
        cr.set_source_rgb(1, 1, 1)

        cr.scale(self.x_scale, self.y_scale)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        self.current_page.render(cr)

    def main(self):
        gtk.main()



if __name__ == "__main__":
    presenter = Presenter()
    presenter.main()

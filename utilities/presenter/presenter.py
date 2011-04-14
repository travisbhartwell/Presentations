#!/usr/bin/python

from twisted.internet import gtk2reactor
gtk2reactor.install()

from functools import partial
import operator

import gtk
import poppler

from twitpic import twitpic2
import twitter

from twisted.web.server import Site
from twisted.web.resource import Resource, NoResource
from twisted.internet import reactor, defer

import config

def generate_commands_page(commands):
    commandsHTML = "<ul>" + \
    "".join( \
        ["<li><a href=\"/%s\">%s</a></li><br><br>" % (command, command) \
         for command in commands.keys()]) + \
    "</ul>"

    return "<html><body>%s</body></html>" % commandsHTML


class PresentationControlCommand(Resource):

    def __init__(self, fn, commands_page_generator):
        Resource.__init__(self)
        self.fn = fn
        self.commands_page_generator = commands_page_generator

    def render_GET(self, _):
        self.fn()
        return self.commands_page_generator()


class LinksCommand(Resource):

    def __init__(self, commands_page_generator):
        Resource.__init__(self)
        self.commands_page_generator = commands_page_generator

    def render_GET(self, _):
        return self.commands_page_generator()


class PresentationControlDispatcher(Resource):

    def __init__(self, commands):
        Resource.__init__(self)

        self.commands = commands
        self.commands_page_generator = partial(generate_commands_page,
                                               self.commands)

    def getChild(self, path, _):
        if path == '':
            return LinksCommand(self.commands_page_generator)
        elif path in self.commands:
            return PresentationControlCommand(self.commands[path],
                                              self.commands_page_generator)
        else:
            return NoResource()


class Presenter(object):

    def __init__(self):
        self.presentation_config = config.presentation

        file_url = "file://%s" % self.presentation_config["slides"]

        self.presentation = \
            poppler.document_new_from_file(file_url, None)
        self.n_pages = self.presentation.get_n_pages()
        self.current_page = self.presentation.get_page(0)

        self.setup_window()

        self.post_slide_deferred = None
        self.posted_slides = []
        self.slides_to_post = self.presentation_config["to_post"]
        self.slide_titles = self.presentation_config["titles"]
        self.image_pattern = self.presentation_config["slide_image_pattern"]

        self.commands = {"next": self.display_next,
                         "previous": self.display_previous,
                         "quit": self.quit}

        # Hack for now to display first slide
        self.display_relative_slide(0, lambda x: True)


    def setup_window(self):
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
        self.display_relative_slide(-1,
                                     lambda p: operator.ge(p, 0))

    def display_next(self):
        self.display_relative_slide(1,
                                    lambda p: operator.lt(p, self.n_pages))

    def post_slide(self, to_post_index):
        slide_number = self.slides_to_post[to_post_index]
        title = self.slide_titles[to_post_index]
        filename = self.image_pattern % slide_number

        print "Now posting slide number %d with title \"%s\"" % (slide_number,
                                                                 title)
        print "\tWith filename: %s" % filename
        response = self.post_to_twitpic(filename, title)

        if response:
            message = "%s: %s" % (response["text"], response["url"])
            self.post_to_twitter(message)

        self.post_slide_deferred = None
        self.posted_slides.append(slide_number)

    def post_to_twitter(self, message):
        api = twitter.Api(consumer_key=config.consumer_key,
                          consumer_secret=config.consumer_secret,
                          access_token_key=config.twitter_oauth_token,
                          access_token_secret=config.twitter_oauth_token_secret)


        api.PostUpdate(message)

    def post_to_twitpic(self, filename, message):
        twitpic = twitpic2.TwitPicOAuthClient(
            consumer_key = config.consumer_key,
            consumer_secret = config.consumer_secret,
            access_token = config.access_token,
            service_key = config.twitpic_api_key,
        )

        response = twitpic.create('upload',
                                  {'media': filename,
                                   "message": message})
        return response


    def display_relative_slide(self, increment, guard):
        current_page_num = self.current_page.get_index()
        next_page_num = current_page_num + increment

        if guard(next_page_num):
            self.current_page = self.presentation.get_page(next_page_num)
            self.dwg.queue_draw()

            if self.post_slide_deferred is not None:
                self.post_slide_deferred.cancel()

            # Only post if we haven't posted before
            if next_page_num not in self.posted_slides:
                try:
                    to_post_index = self.slides_to_post.index(next_page_num)
                    print "Scheduling posting for slide %d" % next_page_num
                    self.post_slide_deferred = defer.Deferred()
                    self.post_slide_deferred.addCallback(self.post_slide)
                    self.post_slide_deferred.addErrback(self.cancel_posting)

                    reactor.callLater(5,
                                      self.post_slide_deferred.callback,
                                      to_post_index)
                except ValueError:
                    print "Not posting slide %d" % next_page_num

    def cancel_posting(self, failure):
        if not failure.check(defer.CancelledError):
            print "Unexpected error:"
            failure.printTraceback()

    def on_key_pressed(self, _, event):
        keyname = gtk.gdk.keyval_name(event.keyval)

        if keyname in ("space", "Return", "Right", "Page_Down"):
            self.display_next()
        elif keyname in ("Left", "Page_Up"):
            self.display_previous()
        elif keyname == "Escape":
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
        root = PresentationControlDispatcher(self.commands)
        factory = Site(root)
        reactor.listenTCP(8888, factory)
        reactor.run()


if __name__ == "__main__":
    presenter = Presenter()
    presenter.main()

# Slides, a HTML slide generator
# Copyright (C) 2002 Moshe Zadka, Itamar Shtull-Trauring
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of version 2.1 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""Slides, a HTML slide generator."""

__version__ = "1.0-post"


import os, string, cgi, types


class Lecture:
    """A series of slides.

    Arguments:
      name -- the name of the presentation, and then pass
      *slides -- Slide instances.
    
    When you're done call renderHTML().
    """
    
    css = None

    def __init__(self, name, *slides):
        self.name = name
	self.slides = slides
        
    def renderHTML(self, directory, basename, css=None):
        """Render all slides and their index.

        Arguments:
          directory -- directory in which to save slides.
          basename -- will be called with % index, so e.g. "slide-%d.html".
          [css] -- path to CSS file to use in output.
        """
        self.css = css
        self.renderSlide(self.slides[0], 1, directory, basename, prev=0)
        for i in range(1, len(self.slides)-1):
            self.renderSlide(self.slides[i], i+1, directory, basename)
        i = len(self.slides)-1
        self.renderSlide(self.slides[i], i+1, directory, basename, next=0)
        self.renderIndex(directory, basename)

    def getHeader(self):
        """Return the header for HTML pages."""
        result = '<html>\n<head>\n<title>%s</title>\n' % cgi.escape(self.name)
        if self.css:
            result += '<link rel="stylesheet" type="text/css" href="%s" />\n' % self.css
        return result + '</head>\n<body>\n'
    
    def getFooter(self):
        """Return the footer for HTML pages."""
        return '<br /><div class="footer"><hr />%s</div></body></html>' % self.name

    def getIndexFooter(self):
        """Return the footer for Index page."""
        return '<br /></body></html>'

    def renderIndex(self, directory, basename):
        """Render the index page of the presentation."""
        fp = open(os.path.join(directory, basename % 0), 'w')
        fp.write(self.getHeader())
        fp.write('<h2>%s</h2>\n' % self.name)
        fp.write('<ol>\n')
        for i in range(len(self.slides)):
            fp.write("<li><a href='%s'>%s</a></li>\n" %
                 (basename % (i+1), self.slides[i].title))
        fp.write('</ol>\n')
        fp.write(self.getIndexFooter())
        fp.close()

    def renderSlide(self, slide, i, directory, basename, prev=1, next=1):
        """Render a single slide."""
        html = slide.toHTML()
        if prev:
            prevName = basename % (i-1)
            prev = '<a accesskey="P" href="%s">Prev</a>' % prevName
        else:
            prev = 'Prev'
        if next:
            nextName = basename % (i+1)
            next = '<a acesskey="N" href="%s">Next</a>' % nextName
        else:
            next = 'Next'
        index = '<a href="%s">Index</a>' % (basename % 0)
        result = (self.getHeader() + " | ".join([prev, index, next]) +
              html + self.getFooter())
        fp = open(os.path.join(directory, basename % i), 'w')
        fp.write(result)
        fp.close()


class Slide:
    """A slide that contains unnumbered bullets.

    Arguments:
      title -- the slide's title.
      *bullets -- Bullet instances.
    """
    
    start = "<ul>\n"
    end = "</ul>\n"
    
    def __init__(self, title, *bullets):
        self.title = title
        self.bullets = bullets

    def toHTML(self):
        title = '<h2>%s</h2>' % cgi.escape(self.title)
        bullets = []
        for bullet in self.bullets:
            bullets.append(bullet.toHTML())
        return title + self.start + string.join(bullets, '\n') + self.end


class NumSlide(Slide):
    """A slide that contains numbered bullets.

    Arguments:
      title -- the slide's title.
      *bullets -- Bullet instances.
    """
    
    start = "<ol>\n"
    end = "</ol>\n"


class SubBullet:
    """A list of bullets that isn't a slide.

    Arguments:
      *bullets -- Bullet instances.
    """
    
    def __init__(self, *bullets):
        self.bullets = bullets

    def toHTML(self):
        bullets = []
        for bullet in self.bullets:
            bullets.append(toHTML(bullet))
        return '<ul>'+string.join(bullets, '\n')+'</ul>'


class Bullet:
    """A bullet."""
    
    def __init__(self, *texts):
        self.texts = texts

    def toHTML(self):        
        return '<li>'+ "".join(map(toHTML, self.texts)) + '</li>\n'


class PRE:
    """A quoted text."""
    
    def __init__(self, text):
        self.text = text

    def toHTML(self):
        return '<pre>\n'+cgi.escape(self.text)+'</pre>'


class URL:
    """A URL."""
    def __init__(self, text):
        self.text = text

    def toHTML(self):
        return '<a href="%s">%s</a>' % (self.text, self.text)


def toHTML(text):
    """Convert string or object to HTML."""
    if isinstance(text, types.StringType):
        return cgi.escape(text)
    else:
        return text.toHTML()


class Heading:
    """A heading of a given level (1, 2, ...)."""
    def __init__(self, num, text):
        self.num = num
        self.text = text

    def toHTML(self):
        return '<h%d>%s</h%d>' % (self.num, toHTML(self.text), self.num)


class Center:
    """Center an item."""
    
    def __init__(self, text):
        self.text = text

    def toHTML(self):
        return '<center>%s</center>' % toHTML(self.text)


class Image:
    """An image."""
    
    def __init__(self, image, description=""):
        self.image = image
        self.description = description
        
    def toHTML(self):
        return "<img src='%s' alt='%s' />" % (self.image, self.description)


class TitleSlide(Slide):

    def toHTML(self):
        title = '<h1>%s</h1>' % toHTML(Center(self.title))
        points = []
        for point in self.bullets:
            points.append(Center(point).toHTML())
        return title + '\n'.join(points)


__all__ = ["Lecture", "Slide", "NumSlide", "PRE", "URL", "Bullet",
           "SubBullet", "toHTML", "Center", "Heading", "Image", "TitleSlide"]

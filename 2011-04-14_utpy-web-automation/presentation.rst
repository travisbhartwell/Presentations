==========================
Web Automation with Python
==========================

:Organization: Utah Python User Group
:Author: Travis B. Hartwell <nafai@travishartwell.net>
:Date: 2011-04-14

Web Automation
==============

To automate things on the web, this is my preferred order:

- Web service APIs using urllib, with higher-level abstractions on top

- Simple web scraping with urllib and BeautifulSoup_

- Automation with Mechanize_, using BeautifulSoup for parsing

- Automating a web browser with Selenium_


.. _BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/
.. _Mechanize: http://wwwsearch.sourceforge.net/mechanize/
.. _Selenium: http://seleniumhq.org

Example: Getting My Latest Twitter Status
=========================================

Here's a simple script for getting my latest Twitter status:

.. code-block:: python

  .. include:: examples/twitter_get_status.py


Example: Higher level wrapper around urllib
===========================================

Sometimes you can make a convenient wrapper around urllib calls:

- twipiclib

- facebook

- gdata


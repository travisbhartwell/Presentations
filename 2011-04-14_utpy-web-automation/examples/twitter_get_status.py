#!/usr/bin/python

import json
import urllib

URL_BASE = "http://twitter.com/statuses/"
STATUS_QUERY = "user_timeline/%s.json?count=1"
URL = URL_BASE + STATUS_QUERY % "travisbhartwell"

status_json = urllib.urlopen(URL).read()
status = json.loads(status_json)
print status[0][u'text']

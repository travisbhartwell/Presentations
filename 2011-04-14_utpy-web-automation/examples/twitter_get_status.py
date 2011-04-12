#!/usr/bin/python

import json
import urllib

URL = "http://twitter.com/statuses/user_timeline/travisbhartwell.json?count=1"

status_json = urllib.urlopen(URL).read()
status = json.loads(status_json)
print status[0][u'text']

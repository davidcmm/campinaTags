#!/usr/bin/python
# https://pythonprogramming.net/creating-first-flask-web-app/
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/campinaTags/")

from campinaTags import app as application
application.secret_key = 'g\x97\xa7M6"\xd5\xdc\xfe~\xc8m|c;z\xb0\x96\x88<\x0b\x89T:'

#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#



import cgi
import wsgiref.handlers
import os
import re

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from django.template import defaultfilters

class Term(db.Model):
  text = db.StringProperty(multiline=False)
  date = db.DateTimeProperty(auto_now_add=True)
  slug = db.StringProperty(multiline=False)

class MainHandler(webapp.RequestHandler):
  def get(self):
    terms = db.GqlQuery("SELECT * FROM Term ORDER BY date DESC")
    template_values = {'terms': terms}
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class CreateHandler(webapp.RequestHandler):
  def post(self):
    text = self.request.get('term')
    slug = self.string_to_slug(text)
    term = Term(key_name = slug)
    term.text = text
    term.put()
    self.redirect("/")

  # slugify for the poor people
  def string_to_slug(self, s):    
    raw_data = s
    raw_data = raw_data.encode("unicode_escape")
    return re.sub(r'[^a-z0-9-]+', '_', raw_data.lower()).strip('_')

class ShowHandler(webapp.RequestHandler):
  def get(self, action=""):
    template_values = { 'term': Term.get_by_key_name(action) }
    path = os.path.join(os.path.dirname(__file__), 'show.html')
    self.response.out.write(template.render(path, template_values))

def main():
  application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/create', CreateHandler),
                                        (r'/show/(.*)', ShowHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()

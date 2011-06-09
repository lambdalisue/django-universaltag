#!/usr/bin/env python
# vim: set fileencoding=utf8 :
"""API URL configuration


Copyright:
    Copyright 2011 Alisue allright reserved.

License:
    Licensed under the Apache License, Version 2.0 (the "License"); 
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unliss required by applicable law or agreed to in writing, software
    distributed under the License is distrubuted on an "AS IS" BASICS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
__author__  = 'Alisue <lambdalisue@hashnote.net>'
__version__ = '1.0.0'
__date__    = '2011/06/09'
from django.conf.urls.defaults import patterns, url
from piston.resource import Resource
from piston.doc import documentation_view

from handlers import TaggedItemHandler

tagged_item_handler = Resource(TaggedItemHandler)

urlpatterns = patterns('',
    url(r'^(?P<content_type>\d+)/(?P<object_id>\d+)/$',                     tagged_item_handler,    name='universaltag-api'),
    url(r'^(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<label>[^/]+)/$',    tagged_item_handler,    name='universaltag-api'),
    
    # Documentation
    url(r'^doc/$',  documentation_view),
)
#!/usr/bin/env python
# vim: set fileencoding=utf8 :
"""The short module explanation.

the long module explanation.
the long module explanation.

Methods:
    foobar - the explanation of the method.

Data:
    hogehoge - the explanation of the data.


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
from django.db import models
from django.contrib.auth.models import User

from universaltag.fields import UniversalTagField

class Entry(models.Model):
    title = models.CharField("title", max_length=128)
    body = models.TextField("body")
    author = models.ForeignKey(User, verbose_name="author")
    tags = UniversalTagField()
    
    def __unicode__(self):
        return self.title
    
    @models.permalink
    def get_absolute_url(self):
        return ('blogs-entry-detail', (self.pk,))
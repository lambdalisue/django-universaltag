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
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from app_test import AppTestCase
from app.models import Book
from ..models import Tag, TaggedItem

import os.path

class GeneralViewTestCase(AppTestCase):
    installed_apps = ['universaltag.tests.app']
    urls = 'universaltag.urls'
    fixtures = ['universaltag_test_data.json',]
    template_dirs = (
        os.path.join(os.path.dirname(__file__), 'templates'),
    )
    
    def setUp(self):
        # Set Test TEMPLATE_DIRS
        self._template_dirs_backup = settings.TEMPLATE_DIRS
        settings.TEMPLATE_DIRS = self.template_dirs
        # Update content_type and book
        self.book = Book.objects.get(pk=1)
        self.book_pk = self.book.pk
        self.book_ct = ContentType.objects.get_for_model(Book).pk
        
    def tearDown(self):
        settings.TEMPLATE_DIRS = self._template_dirs_backup
        
    def test_list(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object_list'].count(), Tag.objects.count())
    
    def test_detail(self):
        response = self.client.get('/tag1/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object'], Tag.objects.get(label='tag1'))
    
    def test_api_get(self):
        url = "/api/%d/%d/" % (self.book_ct, self.book_pk)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
    
    def test_api_post(self):
        url = "/api/%d/%d/" % (self.book_ct, self.book_pk)
        data = {
            'labels': "test1, test2, test3",
        }
        previous_count = Tag.objects.count()
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Tag.objects.count(), previous_count+3)
    
    def test_api_put_sort(self):
        url = "/api/%d/%d/" % (self.book_ct, self.book_pk)
        # Reverse
        labels = ['tag3', 'tag2', 'tag1']
        data = {
            'labels': ", ".join(labels),
        }
        response = self.client.put(url, data)
        self.assertEquals(response.status_code, 200)
        for i, tagged_item in enumerate(TaggedItem.objects.get_for_object(self.book)):
            self.assertEquals(tagged_item.tag.label, labels[i])
        # Re reverse
        labels.reverse()
        data = {
            'labels': ", ".join(labels),
        }
        response = self.client.put(url, data)
        self.assertEquals(response.status_code, 200)
        for i, tagged_item in enumerate(TaggedItem.objects.get_for_object(self.book)):
            self.assertEquals(tagged_item.tag.label, labels[i])
    
    def test_api_put_freeze(self):
        url = "/api/%d/%d/tag1/" % (self.book_ct, self.book_pk)
        
        # Thaw programatically
        tagged_item = TaggedItem.objects.get_by_label(self.book, 'tag1')
        tagged_item.frozen = False
        tagged_item.save()
        
        # Failed for anonymous user
        response = self.client.put(url)
        self.assertEquals(response.status_code, 401)
        
        # Required to be authenticated user
        self.assertTrue(self.client.login(username='admin', password='password'))
        
        # Freeze
        response = self.client.put(url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(TaggedItem.objects.get_by_label(self.book, 'tag1').frozen)
        
        # Thaw
        response = self.client.put(url)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(TaggedItem.objects.get_by_label(self.book, 'tag1').frozen)
    
    def test_api_delete(self):
        # Create New Tag for delete
        TaggedItem.objects.add_or_get(self.book, "delete_test")
        # Delete
        url = "/api/%d/%d/delete_test/" % (self.book_ct, self.book_pk)
        previous_count = TaggedItem.objects.get_for_object(self.book).count()
        
        response = self.client.delete(url)
        self.assertEquals(response.status_code, 204)
        self.assertEquals(TaggedItem.objects.get_for_object(self.book).count(), previous_count-1)

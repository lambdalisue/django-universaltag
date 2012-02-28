#!/usr/bin/env python
# vim: set fileencoding=utf8 :
"""Test module for universaltag models


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
from django.contrib.auth.models import User
from app_test import AppTestCase
from ..models import TaggedItem

class TaggedItemTestCase(AppTestCase):
    installed_apps = ['universaltag.tests.app']
    def setUp(self):
        from app.models import Book
        self.admin = User.objects.create_superuser(
                username='universaltag_test_user', email='universaltag_test_user@test.com',
                password='password'
            )
        self.book1 = Book(pk=1, title="foo", body="foofoofoo", author=self.admin)
        self.book1.save()
        self.book2 = Book(pk=2, title="bar", body="barbarbar", author=self.admin)
        self.book2.save()
    
        # Delete TaggedItem everytime
        TaggedItem.objects.all().delete()
        
    def test_add_or_get(self):
        TaggedItem.objects.add_or_get(self.book1, 'test1')
        TaggedItem.objects.add_or_get(self.book1, 'test2')
        TaggedItem.objects.add_or_get(self.book1, 'test3')
        self.assertEquals(len(self.book1.tags.values()), 3)
    def test_add_or_get_duplicate(self):
        TaggedItem.objects.add_or_get(self.book1, 'test1')
        TaggedItem.objects.add_or_get(self.book1, 'test2')
        TaggedItem.objects.add_or_get(self.book1, 'test3')
        # Add duplicate tag
        TaggedItem.objects.add_or_get(self.book1, 'test3')
        self.assertEquals(len(self.book1.tags.values()), 3)
    def test_get_for_model(self):
        from app.models import Book
        TaggedItem.objects.add_or_get(self.book1, 'test1')
        TaggedItem.objects.add_or_get(self.book1, 'test2')
        TaggedItem.objects.add_or_get(self.book1, 'test3')
        TaggedItem.objects.add_or_get(self.book2, 'test2')
        TaggedItem.objects.add_or_get(self.book2, 'test3')
        TaggedItem.objects.add_or_get(self.book2, 'test4')

        qs = TaggedItem.objects.get_for_model(Book)
        self.assertEquals(qs.count(), 6)
    def test_get_for_object(self):
        TaggedItem.objects.add_or_get(self.book1, 'test1')
        TaggedItem.objects.add_or_get(self.book1, 'test2')
        TaggedItem.objects.add_or_get(self.book1, 'test3')
        TaggedItem.objects.add_or_get(self.book2, 'test2')
        TaggedItem.objects.add_or_get(self.book2, 'test3')
        TaggedItem.objects.add_or_get(self.book2, 'test4')

        qs = TaggedItem.objects.get_for_object(self.book1)
        self.assertEquals(qs.count(), 3)
    def test_remove(self):
        TaggedItem.objects.add_or_get(self.book1, 'test1')
        TaggedItem.objects.add_or_get(self.book1, 'test2')
        TaggedItem.objects.add_or_get(self.book1, 'test3')

        qs = TaggedItem.objects.get_for_object(self.book1)
        self.assertEquals(qs.count(), 3)
        
        TaggedItem.objects.remove(self.book1, 'test1')
        
        qs = TaggedItem.objects.get_for_object(self.book1)
        self.assertEquals(qs.count(), 2)
        
    def test_freeze(self):
        TaggedItem.objects.add_or_get(self.book1, 'test1')
        TaggedItem.objects.add_or_get(self.book1, 'test2')
        TaggedItem.objects.add_or_get(self.book1, 'test3')
        
        TaggedItem.objects.freeze(self.book1, 'test1', 'thaw')
        
        tagged_item = TaggedItem.objects.get_for_object(self.book1).get(tag__label='test1')
        self.assertFalse(tagged_item.frozen)

        TaggedItem.objects.freeze(self.book1, 'test1')
        
        tagged_item = TaggedItem.objects.get_for_object(self.book1).get(tag__label='test1')
        self.assertTrue(tagged_item.frozen)
        
        TaggedItem.objects.freeze(self.book1, 'test1')
        
        tagged_item = TaggedItem.objects.get_for_object(self.book1).get(tag__label='test1')
        self.assertFalse(tagged_item.frozen)
    
    def test_remove_fail(self):
        TaggedItem.objects.add_or_get(self.book1, 'test1')
        TaggedItem.objects.add_or_get(self.book1, 'test2')
        TaggedItem.objects.add_or_get(self.book1, 'test3')
        
        TaggedItem.objects.freeze(self.book1, 'test1', 'freeze')
        TaggedItem.objects.remove(self.book1, 'test1')
        
        qs = TaggedItem.objects.get_for_object(self.book1)
        self.assertEquals(qs.count(), 3)
        
        TaggedItem.objects.freeze(self.book1, 'test1', 'thaw')
        TaggedItem.objects.remove(self.book1, 'test1')
        
        qs = TaggedItem.objects.get_for_object(self.book1)
        self.assertEquals(qs.count(), 2)
    
    def test_reconstruct(self):
        TaggedItem.objects.add_or_get(self.book1, 'test1')
        TaggedItem.objects.add_or_get(self.book1, 'test2')
        TaggedItem.objects.add_or_get(self.book1, 'test3')
        
        NEW_TAGS = ("foobar1", "foobar2", "foobar3", "foobar4")
        TaggedItem.objects.reconstruct(self.book1, ",".join(NEW_TAGS))
        
        qs = TaggedItem.objects.get_for_object(self.book1)
        for i, tagged_item in enumerate(qs):
            self.assertEquals(tagged_item.tag.label, NEW_TAGS[i])


        

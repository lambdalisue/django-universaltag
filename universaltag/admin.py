#!/usr/bin/env python
# vim: set fileencoding=utf8 :
"""Admin config for universaltag


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
from django.contrib import admin
from django.utils.text import ugettext_lazy as _

from models import Tag, TaggedItem

class TagAdmin(admin.ModelAdmin):
    """Admin configure for Tag model"""
    list_display    = ('__unicode__', 'number_of_items',)
    search_fields   = ('label',)
    
    def number_of_items(self, obj):
        return len(obj.items.iterators)
    number_of_items.short_description = _("Number of items")
    
class TaggedItemAdmin(admin.ModelAdmin):
    """Admin configure for TaggedItem model"""
    list_display    = ('__unicode__', 'content_object', 'content_type', 'frozen', 'order')
    list_filter     = ('content_type', 'frozen',)

admin.site.register(Tag, TagAdmin)
admin.site.register(TaggedItem, TaggedItemAdmin)

#!/usr/bin/env python
# vim: set fileencoding=utf8 :
"""django_filters Filter class for universaltag

`django_filters` is a generic system for filtering Django QuerySets based on user selection.
See https://github.com/alex/django-filter for more detail.


Classes:
    ModeltagFilter - a custom filter for modeltag
    

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
from django import forms
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from models import Tag
from utils import parse_tag_input

from django_filters import filters

    
class UniversalTagFilter(filters.ChoiceFilter):
    """
    This filter preforms an OR query on the selected options.
    """
    field_class = forms.ChoiceField
    def __init__(self, threshold=1, *args, **kwargs):
        """Constructor
        
        Args:
            threshold - threshold of number of tags. tags under it ignored to display
        """
        self.threshold = threshold
        super(UniversalTagFilter, self).__init__(*args, **kwargs)
        
    @property
    def field(self):
        qs = Tag.objects.get_for_model(self.model).annotate(count=Count('items')).exclude(count__lt=self.threshold).order_by('-count')
        choices = [['', _('All')]] + [(tag.pk, tag.label) for tag in qs]
        self.extra['choices'] = tuple(choices)
        return super(UniversalTagFilter, self).field
    
    def filter(self, qs, value):
        if not value:
            return qs
        if isinstance(value, basestring):
            value = parse_tag_input(value)
        elif not isinstance(value, list) and not isinstance(value, tuple):
            value = [value]
        return qs.filter(**{"%s__tag__pk__in"%self.name: value}).distinct()
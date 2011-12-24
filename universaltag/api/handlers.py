#!/usr/bin/env python
# vim: set fileencoding=utf8 :
"""API module of universaltag via piston


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
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from piston.handler import BaseHandler
from piston.utils import rc, validate, throttle

from ..models import TaggedItem
from ..utils import parse_tag_input
from ..exceptions import DuplicateError

class ValidationPOSTForm(forms.Form):
    """Form for POST validation"""
    labels = forms.CharField()
class ValidationPUTForm(forms.Form):
    """Form for PUT validation"""
    labels = forms.CharField(required=False)

def get_or_not_found(fn):
    """Get and set object or return rc.NOT_FOUND decorator
    
    Get object instance from content_type and object_id and set it to request.obj
    and call decorated function, or return rc.NOT_FOUND when object could not be found
    """
    def wrapper(self, request, content_type, object_id, *args, **kwargs):
        try:
            ctype = get_object_or_404(ContentType, pk=content_type)
            obj = ctype.get_object_for_this_type(pk=object_id)
            request.obj = obj
            return fn(self, request, content_type, object_id, *args, **kwargs)
        except (Http404, ObjectDoesNotExist):
            return rc.NOT_FOUND
    return wrapper

class TaggedItemHandler(BaseHandler):
    """TaggedItem piston handler"""
    allowed_method = ('GET', 'POST', 'PUT', 'DELETE')
    model = TaggedItem
    fields = (
        'pk',
        ('tag', ('pk', 'label', 'absolute_uri')),
        'frozen', 'order',
        'absolute_uri'
    )
    
    @get_or_not_found
    def read(self, request, content_type, object_id, label=None):
        qs = self.model.objects.get_for_object(request.obj)
        if label:
            return qs.get(tag__label=label)
        return qs
    
    @get_or_not_found
    @validate(ValidationPOSTForm, 'POST')
    @throttle(100, 10*60)
    def create(self, request, content_type, object_id):
        labels = parse_tag_input(request.form.cleaned_data['labels'])
        instance_list = []
        for label in labels:
            if len(label) > settings.UNIVERSALTAG_TAG_LENGTH:
                continue
            try:
                instance_list.append(self.model.objects.add_or_get(request.obj, label, False))
            except DuplicateError:
                pass
        return instance_list
    
    @get_or_not_found
    @validate(ValidationPUTForm, 'PUT')
    @throttle(100, 10*60)
    def update(self, request, content_type, object_id, label=None):
        if not label:
            # Sort tags via order of appearance in labels
            labels = parse_tag_input(request.form.cleaned_data['labels'])
            for i, label in enumerate(labels):
                tagged_item = self.model.objects.add_or_get(request.obj, label)
                tagged_item.order = i
                tagged_item.save()
            return TaggedItem.objects.get_for_object(request.obj)
        else:
            # Toggle tag freeze status
            # Only author of obj can freeze/thaw tag
            if hasattr(request, 'user') and request.user.is_authenticated():
                if request.user.is_superuser:
                    return self.model.objects.freeze(request.obj, label)
                for attr in settings.UNIVERSALTAG_AUTHOR_ATTRS:
                    if getattr(request.obj, attr, None) == request.user:
                        return self.model.objects.freeze(request.obj, label)
            return rc.FORBIDDEN
        
    @get_or_not_found
    @throttle(100, 10*60)
    def delete(self, request, content_type, object_id, label):
        if self.model.objects.remove(request.obj, label) is None:
            # Tried to delete frozen tag
            return rc.FORBIDDEN
        # Successfully deleted
        return rc.DELETED

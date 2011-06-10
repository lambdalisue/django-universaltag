#!/usr/bin/env python
# vim: set fileencoding=utf8 :
"""Template tags module for universaltag


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
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.template import TemplateSyntaxError
from django.contrib.contenttypes.models import ContentType

from ..models import Tag, TaggedItem

register = template.Library()
    
class RenderUniversalTagHeadNode(template.Node):
    def render(self, context):
        suggestions = Tag.objects.all()
        context.push()
        html = render_to_string('universaltag/head.html', {'suggestions': suggestions}, context)
        context.pop()
        return html
    
class RenderUniversalTagNode(template.Node):
    def __init__(self, object, threshold=None):
        self.object = template.Variable(object)
        self.threshold = template.Variable(threshold) if threshold else None
        
    def render(self, context):
        def is_freezable(request, object):
            if hasattr(request, 'user') and request.user.is_authenticated():
                if request.user.is_superuser:
                    return True
                for attr in settings.UNIVERSALTAG_AUTHOR_ATTRS:
                    if getattr(object, attr, None) == request.user:
                        return True
            return False
        request = template.resolve_variable('request', context)
        object = self.object.resolve(context)
        
        tagged_items = TaggedItem.objects.get_for_object(object)
        ctype = ContentType.objects.get_for_model(object)
        # Threshold
        if self.threshold:
            threshold = self.threshold.resolve(context)
            tagged_items = tagged_items[:threshold]
        # HTML
        context.push()
        kwargs = {
            'tagged_items': tagged_items,
            'universaltag_api_url': reverse('universaltag-api', args=(ctype.pk, object.pk)),
            'is_freezable': is_freezable(request, object),
        }
        html = render_to_string('universaltag/list.html', kwargs, context)
        context.pop()
        return html

class GetUniversalTagAPIURLNode(template.Node):
    def __init__(self, object, variable):
        self.object = template.Variable(object)
        self.variable = variable
    
    def render(self, context):
        object = self.object.resolve(context)
        ctype = ContentType.objects.get_for_model(object)
        context[self.variable] = reverse("universaltag-api", args=(ctype.pk, object.pk))
        return ""
                                  
@register.tag
def render_universaltag_tags(parser, token):
    """Render universaltag list as ul list
    
    Usage:
        {% render_universaltag_tags of <object> %}
        {% render_universaltag_tags of <object> threshold <threshold> %}
        
    """
    bits = token.split_contents()
    if len(bits) == 5:
        if bits[1] != 'of':
            raise TemplateSyntaxError("first argument of %s tag must be 'of'" % bits[0])
        elif bits[3] != 'threshold':
            raise TemplateSyntaxError("third argument of %s tag must be 'threshold'" % bits[0])
        return RenderUniversalTagNode(bits[2], bits[4])
    elif len(bits) == 3:
        if bits[1] != 'of':
            raise TemplateSyntaxError("first argument of %s tag must be 'of'" % bits[0])
        return RenderUniversalTagNode(bits[2])
    raise TemplateSyntaxError("%s tag takes exactly 3 or 5 arguments." % bits[0])

@register.tag
def render_universaltag_head(parser, token):
    """Render javascript and css to be able the feature of editing tags
    
    Use this template tag in head block to be able the feature of editing tags.
    
    Syntax:
        {% render_universaltag_head %}
    """
    bits = token.split_contents()
    if len(bits) == 1:
        return RenderUniversalTagHeadNode()
    raise TemplateSyntaxError("%s tag never takes any arguments." % bits[0])

@register.tag
def get_universaltag_api_url(parser, token):
    """Get universaltag api url
    
    Usage:
        {% get_universaltag_api_url of <object> to <variable> %}
        
    """
    bits = token.split_contents()
    if len(bits) == 5:
        if bits[1] != 'of':
            raise TemplateSyntaxError("first argument of %s tag must be 'of'" % bits[0])
        elif bits[3] != 'to':
            raise TemplateSyntaxError("third argument of %s tag must be 'to'" % bits[0])
        return GetUniversalTagAPIURLNode(bits[2], bits[4])
    raise TemplateSyntaxError("%s tag takes exactly 5 arguments." % bits[0])
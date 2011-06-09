#!/usr/bin/env python
# vim: set fileencoding=utf8 :
"""Field module for universaltag

Classes:
    UniversalTagField - TaggedItem field for model
    

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
from django.contrib.contenttypes.generic import GenericRelation
from models import TaggedItem

class UniversalTagField(GenericRelation):
    """TaggedItem field for model (Reverse generic relation)
    
    Usage:
        >>> from django.db import models
        >>> class Book(models.Model):
        ...     title = models.CharField("title", max_length=50)
        ...     body = models.TextField("body")
        ...     tags = UniversalTagField()
        
    """
    def __init__(self, **kwargs):
        if not 'to' in kwargs:
            kwargs['to'] = TaggedItem
        super(UniversalTagField, self).__init__(**kwargs)

try:
    # Accept migration via south
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], [r'universaltag.fields.UniversalTagField'])
except ImportError:
    pass

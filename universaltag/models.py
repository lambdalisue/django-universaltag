#!/usr/bin/env python
# vim: set fileencoding=utf8 :
"""Model module for universaltag

Classes:
    TagManager - a manager class of tag
    TaggedItemManager - a manager class of tagged item
    Tag - a model class of tag
    TaggedItem - a bridge model class of tag and model

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
from django.db.models import Max
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from exceptions import DuplicateError, NotDeletableError
from utils import parse_tag_input

class TagManager(models.Manager):
    """Manager class of tag model"""
        
    def get_for_model(self, model):
        """Return tags related to the model"""
        ctype = ContentType.objects.get_for_model(model)
        return self.filter(items__content_type=ctype).distinct()
    
    def get_for_object(self, obj):
        """Return tags related to the obj"""
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(items__content_type=ctype, items__object_id=obj.pk).distinct().order_by('items__order')
    
class TaggedItemManager(models.Manager):
    """Model manager for TaggedItem"""
    
    def get_by_label(self, obj, label):
        """Get tagged item by label"""
        qs = self.get_for_object(obj)
        return qs.get(tag__label=label)
    
    def get_for_model(self, model):
        """Return tagged_items related to the model"""
        ctype = ContentType.objects.get_for_model(model)
        return self.filter(content_type=ctype).distinct()
    
    def get_for_object(self, obj):
        """Return tagged_items related to the obj"""
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=ctype, object_id=obj.pk).distinct().order_by('order')

    def add_or_get(self, obj, label, ignore_duplication=True):
        """Add or get tag to obj and return TaggedItem instance
        
        Args:
            obj - the target model instance
            label - a label of tag
            ignore_duplication - if it False, DuplicateError occur when the label tag is already registered.
        
        Return:
            TaggedItem instance
        """
        ct = ContentType.objects.get_for_model(obj)
        tag = Tag.objects.get_or_create(label=label)[0]
        # Get or Create
        tagged_item, created = self.get_or_create(tag=tag, content_type=ct, object_id=obj.pk)
        if not created and not ignore_duplication:
            raise DuplicateError('%s is already related to the object' % label)
        return tagged_item
    
    def remove(self, obj, label, ignore_undeletable=True):
        """Remove label from the obj and return TaggedItem
        
        If the label is not related to any obj, the label will be removed as well.
        
        Args:
            obj - the target model instance
            label - a label of tag
        
        Return:
            TaggedItem instance - removed TaggedItem instance (instance.pk is None)
        """
        tagged_item = self.get_for_object(obj).get(tag__label=label)
        if tagged_item.frozen:
            if not ignore_undeletable:
                raise NotDeletableError("%s is a frozen tag for the object. couldn't remove." % label)
            else:
                return None
        else:
            tagged_item.delete()
            if tagged_item.tag.items.count() == 0:
                # Remove tag as well
                tagged_item.tag.delete()
        return tagged_item
            
    
    def freeze(self, obj, label, action=None):
        """Freeze or thaw label tag related to the obj
        
        Args:
            obj - the target model instance
            label - a label of tag
            action - None for toggle, `freeze` for freeze and `thaw` for thaw.
        
        Return:
            TaggedItem instance
        """
        tagged_item = self.get_for_object(obj).get(tag__label=label)
        if action == 'thaw' or (tagged_item.frozen and action is None):
            tagged_item.frozen = False
        elif action == 'freeze' or (not tagged_item.frozen and action is None):
            tagged_item.frozen = True
        tagged_item.save()
        return tagged_item
    
    def reconstruct(self, obj, labels):
        """Reconstruct tags for object via label list
        
        Args:
            obj - the target model instance
            labels - a list of tag label
        """
        ctype = ContentType.objects.get_for_model(obj)
        current_tags = list(Tag.objects.filter(items__content_type=ctype, items__object_id=obj.pk))
        updated_tag_labels = parse_tag_input(labels)
        # Remove all tags not in updated_tag_labels
        tags_for_removal = [tag for tag in current_tags if tag.label not in updated_tag_labels]
        if len(tags_for_removal):
            self.filter(
                content_type=ctype,
                object_id=obj.pk,
                tag__in=tags_for_removal).delete()
        # Append new tags
        current_tag_labels = [tag.label for tag in current_tags]
        for tag_label in updated_tag_labels:
            if not tag_label in current_tag_labels:
                self.add_or_get(obj, tag_label)
                
class Tag(models.Model):
    """Actual individual universaltag model"""
    label       = models.CharField(_('label'), 
                                   max_length=settings.UNIVERSALTAG_TAG_LENGTH, 
                                   unique=True, db_index=True)
    
    objects     = TagManager()
    
    class Meta:
        ordering            = ('label',)
        verbose_name        = _('tag')
        verbose_name_plural = _('tags')

    def __unicode__(self):
        return self.label
    
    @models.permalink
    def get_absolute_url(self):
        return ('universaltag-tag-detail', (self.label,))

class TaggedItem(models.Model):
    """Bridge model of tag and model with generic relation."""
    tag             = models.ForeignKey(Tag, verbose_name=_('tag'), related_name='items')
    content_type    = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id       = models.PositiveIntegerField(_('object ID'))
    content_object  = generic.GenericForeignKey(ct_field="content_type", fk_field="object_id")
    
    # TODO: shoud be 'lock'
    frozen          = models.BooleanField(_('is not deletable'), default=False)
    # TODO: should use django's ordering system (May not usable, so have to find
    # out)
    order           = models.IntegerField(_('order'), default=-1, blank=True)
    
    objects         = TaggedItemManager()
    
    class Meta:
        ordering            = ('order',)
        unique_together     = ('tag', 'content_type', 'object_id')
        verbose_name        = _('tagged item')
        verbose_name_plural = _('tagged items')

    def __unicode__(self):
        return self.tag.__unicode__()

    def save(self, *args, **kwargs):
        # Automatically increment order
        if self.order == -1:
            queryset = TaggedItem.objects.get_for_object(self.content_object)
            if queryset.count() > 0:
                dict = queryset.aggregate(max=Max('order'))
                self.order = dict['max'] + 1
            else:
                self.order = 0
        super(TaggedItem, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Return permalink of object related."""
        if hasattr(self.content_object, 'get_absolute_url'):
            return self.content_object.get_absolute_url()
        return ""
    
    @models.permalink
    def get_api_url(self):
        return ("universaltag-api", (self.content_type.pk, self.object_id))

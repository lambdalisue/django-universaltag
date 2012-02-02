#!/usr/bin/env python
# vim: set fileencoding=utf8:
"""
Django App TestCase


AUTHOR:
    lambdalisue[Ali su ae] (lambdalisue@hashnote.net)
    
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
__AUTHOR__ = "lambdalisue (lambdalisue@hashnote.net)"
from django import test
from django.conf import settings
from django.core.management import call_command
from django.db.models import loading
from django.contrib.contenttypes.models import ContentType

class AppTestCase(test.TestCase):
    installed_apps = []
    middleware_classes = []

    def _get_installed_apps(self):
        # ContentType is required so add
        self.installed_apps.append('django.contrib.contenttypes')
        _installed_apps = list(settings.INSTALLED_APPS)
        for app in self.installed_apps:
            if app not in _installed_apps:
                _installed_apps.append(app)
        return _installed_apps
    def _get_middleware_classes(self):
        _middleware_classes = list(settings.MIDDLEWARE_CLASSES)
        for middleware_class in self.middleware_classes:
            if middleware_class not in _middleware_classes:
                _middleware_classes.append(middleware_class)
        return _middleware_classes

    def _clear_all_meta_caches(self):
        def clear_meta_caches(meta):
            CACHE_NAMES = (
                '_m2m_cache',
                '_field_cache',
                '_name_map',
                '_related_objects_cache',
                '_related_many_to_many_cache',
            )
            for cache_name in CACHE_NAMES:
                if hasattr(meta, cache_name):
                    delattr(meta, cache_name)
        for ct in ContentType.objects.iterator():
            meta = ct.model_class()._meta
            clear_meta_caches(meta)

    def _pre_setup(self):
        # store original installed apps/middleware classes
        self._original_installed_apps = list(settings.INSTALLED_APPS)
        self._original_middleware_classes = list(settings.MIDDLEWARE_CLASSES)
        # get extra required apps and middleware
        settings.INSTALLED_APPS = self._get_installed_apps()
        settings.MIDDLEWARE_CLASSES = self._get_middleware_classes()
        # Call syncdb to create db for extra apps (migrate=False for South)
        loading.cache.loaded = False
        call_command('syncdb', interactive=False, verbosity=0, migrate=False)
        # Call the original method that does the fixtures etc.
        super(AppTestCase, self)._pre_setup()

        # Clear cache of meta of all models
        self._clear_all_meta_caches()

    def _post_teardown(self):
        # Call the original method
        super(AppTestCase, self)._post_teardown()
        # Restore the settings
        settings.INSTALLED_APPS = self._original_installed_apps
        settings.MIDDLEWARE_CLASSES = self._original_middleware_classes
        loading.cache.loaded = False

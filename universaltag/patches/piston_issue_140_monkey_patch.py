#
# Monkey Patch for fixing django-piston issue#140: 'GenericForeignKey' object has no attribute 'serialize'
# Load this module on app/project '__init__.py' as the following code to fix the issue.
#
#   from piston_issue_140_monkey_patch import *
#
# See comment#9 of the issue 
# https://bitbucket.org/jespern/django-piston/issue/140/genericforeignkey-object-has-no-attribute#comment-357757
from django.contrib.contenttypes.generic import GenericForeignKey
GenericForeignKey.serialize = None

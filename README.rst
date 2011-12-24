``django-universaltag`` is a package for tagging Django models object universally.

This package is developing under https://github.com/lambdalisue/django-universaltag

See http://demos.django-universaltag.hashnote.net/ for Demo.

Required
==================

+   `django-piston <https://bitbucket.org/jespern/django-piston>`_

Features
==================

+   Using GenericRelation for relation so a tag can belong to any Django model object
+   Anonymous user can add, delete tags as many as they want
+   Author (object which a tag belong) can protect tag from deleting
+   Nice Ajax add, delete, lock, sort function

See demo for more detail.

Install
=================
::
    $ sudo pip install django-universaltag

or::

    $ sudo pip install git+git://github.com/lambdalisue/django-universaltag#egg=django-universaltag

How to use
=================================================
See https://github.com/lambdalisue/django-universaltag/tree/master/universaltag_test source code for detail.

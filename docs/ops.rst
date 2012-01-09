============================
Systems Administration (Ops)
============================

If you are an advanced user and you're going to run a PANDA server, you may want to know how it all works. This page lays out the users, services and files that are part of the standard PANDA setup.

This might also be thought of as a guide to what you may need to change in the event you want to run PANDA in a non-standard configuration.

Users
=====

panda
-----

Runs the ``uwsgi`` and ``celeryd`` services and owns their logs. Owns ``/var/lib/panda/media`` (compressed assets) and ``/var/lib/panda/uploads`` (uploaded files). Only this user should be used to execute Django management commands, etc::

    sudo -u panda -E python manage.py shell

postgres
--------

Runs the ``postgresql`` service and owns its database files and logs.

root
----

Owns everything else, including the panda source code in ``/opt/panda``.

solr
----

Runs the ``solr`` service and owns its files (``/opt/solr``), indices and logs. 

ubuntu
------

The standard Ubuntu login user. Must be used to SSH into the system and run sudo. Has read-only access to files and logs, but can not execute any system commands.

www-data
--------

Runs the ``nginx`` service and owns its logs.

Services
========

celeryd
-------

Task processing.

nginx
-----

Web server. Runs on port 80.

postgresql
----------

Database. Runs on port 5432 locally. Not accessible from remote hosts. 

solr
----

Search engine. Runs on 8983. Not accessible from remote hosts. 

uwsgi
-----

Python application server. Runs over a socket at ``/var/run/uwsgi/wsgi.sock``.

Files
=====

* ``/var/lib/panda/media`` - compressed assets
* ``/var/lib/panda/uploads`` - file uploads
* ``/opt/panda`` - application source code
* ``/opt/solr`` - Solr application
* ``/var/log/celeryd`` - destination for celery logs if output was not captured and routed to panda logs (exists only as a failsafe)
* ``/var/log/nginx`` - destination for access logs
* ``/var/log/panda`` - destination for application logs (errors and task processing)
* ``/var/log/uwsgi.log`` - destination for uwsgi logs (normally just startup and shutdown)


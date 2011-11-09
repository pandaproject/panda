=================
API Documentation
=================

The PANDA application is built on top of a REST API that can be used to power custom applications or import/export data in novel ways.

The PANDA API follows the conventions of `Tastypie <https://github.com/toastdriven/django-tastypie>`_ as closely as possible. Until more complete documentation is ready, please refer to Tastypie's documentation on `Interacting with the API <http://django-tastypie.readthedocs.org/en/latest/interacting.html>`_ to become familiar with the common idiom.

The following example URLs assuming your running a local development environment. For a production environment replace ``localhost:8000`` with your domain name. If making requests from the command line the ``format=json`` query-string is not necessary.

Tasks
=====

Schema
------

http://localhost:8000/api/1.0/task/schema/?format=json

List
----

http://localhost:8000/api/1.0/task/?format=json

List tasks with a specific status
---------------------------------

http://localhost:8000/api/1.0/task/?format=json&status=PENDING

This list tasks that are queued, but have not yet started processing.

List tasks that finished processing today
-----------------------------------------

http://localhost:8000/api/1.0/task/?format=json&end__year=2011&end__month=10&end__day=31

This list tasks that ended on October 31st, 2011.

Fetch
-----

http://localhost:8000/api/1.0/task/[id]/?format=json

Uploads
=======

Due to limitations in upload file-handling, it is not possible to create Uploads via the normal API. Instead file should be uploaded to http://localhost:8000/upload/ either as form data or as an AJAX request. Examples of how to upload files with curl are at the end of this section.

Schema
------

http://localhost:8000/api/1.0/upload/schema/?format=json

List
----

http://localhost:8000/api/1.0/upload/?format=json

Filtering is currently not supported.

Fetch
-----

http://localhost:8000/api/1.0/upload/[id]/?format=json

Download original file
----------------------

http://localhost:8000/api/1.0/upload/[id]/download/?format=json

Upload as form-data
-------------------

``curl -F file=@README.csv http://localhost:8000/upload/``

Upload via AJAX
---------------

``curl --data-binary @test.csv -H "X-Requested-With:XMLHttpRequest" http://localhost:8000/upload/?qqfile=test.csv``

Datasets
========

Schema
------

http://localhost:8000/api/1.0/dataset/schema/?format=json

List
----

http://localhost:8000/api/1.0/dataset/?format=json

Fetch
-----

http://localhost:8000/api/1.0/dataset/[id]/?format=json

Import
------

http://localhost:8000/api/1.0/dataset/[id]/import/?format=json

Will begin an import task using the dataset's current schema. Any data previously imported for this dataset will be lost. Returns the original dataset, which will include the id of the new import task.

Search
------

http://localhost:8000/api/1.0/dataset/[id]/search/?q=[query]&format=json

Searches for Data within this particular dataset. The response is a simplified Dataset object with added paging ("meta") data and embedded Data instances ("objects").

Data
========

Schema
------

http://localhost:8000/api/1.0/data/schema/?format=json

List
----

http://localhost:8000/api/1.0/data/?format=json

Fetch
-----

http://localhost:8000/api/1.0/data/[id]/?format=json

Search
------

http://localhost:8000/api/1.0/data/[id]?q=[query]&format=json

Searches for Data within all Datasets. The response is an "meta" object with paging information for the matching datasets and an "objects" array which contains simplified Dataset objects and embedded search results identical to the per-Dataset search results.

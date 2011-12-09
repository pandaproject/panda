=================
API Documentation
=================

The PANDA application is built on top of a REST API that can be used to power custom applications or import/export data in novel ways.

The PANDA API follows the conventions of `Tastypie <https://github.com/toastdriven/django-tastypie>`_ except in important cases where doing so would create unacceptable limitations. If this documentation seems incomplete, refer to Tastypie's page on `Interacting with the API <http://django-tastypie.readthedocs.org/en/latest/interacting.html>`_ to become familiar with the common idiom.

.. note::

    You will probably want to try these URLs in your browser. In order to make them work you'll need to use the ``format``, ``username``, and ``api_key`` query string parameters. For example, to authenticate as the default administrative user that comes with PANDA, append the following query string to any url described on this page::

        ?format=json&username=panda&api_key=edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b

All endpoints that return lists support the ``limit`` and ``offset`` parameters for pagination. Pagination information is always returned in the ``meta`` attribute.

Users
=====

The user model can be queried to retrieve information about PANDA users, however, passwords and API keys are not included in responses.

Schema
------

::

    http://localhost:8000/api/1.0/user/schema/

List
----

::

    http://localhost:8000/api/1.0/user/

Fetch
-----

::

    http://localhost:8000/api/1.0/user/[id]/

Create
------

To create a new user, POST a JSON document containing at least ``username`` and ``email`` properties to http://localhost:8000/api/1.0/user/. Other properties such as ``first_name`` and ``last_name`` may also be set. If a ``password`` property is specified it will be set on the new user, but it will not be included in the response. If ``password`` is omitted the user will need to set a password before they can log in (not yet implemented).

Tasks
=====

Schema
------

::

    http://localhost:8000/api/1.0/task/schema/

List
----

::

    http://localhost:8000/api/1.0/task/

List filtered by status 
-----------------------

List tasks that are PENDING (queued, but have not yet started processing)::

    http://localhost:8000/api/1.0/task/?status=PENDING


List filtered by date
---------------------

List tasks that ended on October 31st, 2011::

    http://localhost:8000/api/1.0/task/?end__year=2011&end__month=10&end__day=31

Fetch
-----

::

    http://localhost:8000/api/1.0/task/[id]/

Uploads
=======

Due to limitations in upload file-handling, it is not possible to create Uploads via the normal API. Instead file should be uploaded to http://localhost:8000/upload/ either as form data or as an AJAX request. Examples of how to upload files with curl are at the end of this section.

Schema
------

::

    http://localhost:8000/api/1.0/upload/schema/

List
----

::

    http://localhost:8000/api/1.0/upload/

Filtering is currently not supported.

Fetch
-----

::

    http://localhost:8000/api/1.0/upload/[id]/

Download original file
----------------------

::

    http://localhost:8000/api/1.0/upload/[id]/download/

Upload as form-data
-------------------

When accessing PANDA via curl, your username and API key can be specified with the headers ``PANDA_USERNAME`` and ``PANDA_API_KEY``, respectively::

    curl -H "PANDA_USERNAME: panda" -H "PANDA_API_KEY: edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b" -F file=@README.csv http://localhost:8000/upload/

Upload via AJAX
---------------

::

    curl -H "PANDA_USERNAME: panda" -H "PANDA_API_KEY: edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b" --data-binary @test.csv -H "X-Requested-With:XMLHttpRequest" http://localhost:8000/upload/?qqfile=test.csv

Categories
==========

Categories are referenced by slug, rather than integer id.

Schema
------

::

    http://localhost:8000/api/1.0/category/schema/

List
----

::

    http://localhost:8000/api/1.0/category/

Fetch
-----

::

    http://localhost:8000/api/1.0/category/[slug]/

Datasets
========

Datasets are referenced by slug, rather than integer id.

Schema
------

::

    http://localhost:8000/api/1.0/dataset/schema/

List
----

::
    
    http://localhost:8000/api/1.0/dataset/

List filtered by category
-------------------------

::

    http://localhost:8000/api/1.0/dataset/?category=[slug]

Search for datasets
-------------------

The Dataset list endpoint is overloaded to provide full-text search over metadata. By default this returns complete Dataset objects. To return simplified objects suitable for rendering lists add ``simple=true`` to the query::

    http://localhost:8000/api/1.0/dataset/?q=[query]

Fetch
-----

::

    http://localhost:8000/api/1.0/dataset/[slug]/

Create
------

To create a new Dataset, POST a JSON document containing at least ``name`` and ``data_upload`` properties to ``http://localhost:8000/api/1.0/dataset/``. The ``data_upload`` property may be either an embedded Upload object, or a URI to an existing Upload (for example, ``/api/1.0/upload/17/``). Other properties such as ``description`` may also be set.

Import
------

Begin an import task using the dataset's current schema. Any data previously imported for this dataset will be lost. Returns the original dataset, which will include the id of the new import task::

    http://localhost:8000/api/1.0/dataset/[id]/import/

Search within dataset
---------------------

Search for Data within one particular dataset. The response is a simplified Dataset object with added paging ("meta") data and embedded Data instances ("objects")::

    http://localhost:8000/api/1.0/dataset/[slug]/search/?q=[query]

Data
========

Data are referenced by UUIDs, rather than integer id.

Schema
------

::

    http://localhost:8000/api/1.0/data/schema/

List
----

::

    http://localhost:8000/api/1.0/data/

Fetch
-----

::

    http://localhost:8000/api/1.0/data/[uuid]/

Search
------

Searches for Data within all Datasets. The response is a list of "meta" object with paging information for the matching datasets and an "objects" array which contains simplified **Dataset** objects and embedded search results in the same format as the per-Dataset search results.

Note that when using this endpoint the ``limit`` and ``offset`` parameters refer to the groups returned. If you wish to paginate the result sets of each dataset you can use ``group_limit`` and ``group_offset`` although this is typically not the behavior a user would expect.

::

    http://localhost:8000/api/1.0/data/?q=[query]


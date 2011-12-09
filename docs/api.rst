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

The Task API is read-only.

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

.. note::

    Possible task statuses are ``PENDING``, ``STARTED``, ``SUCCESS``, and ``FAILURE``.


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

    curl -H "PANDA_USERNAME: panda" -H "PANDA_API_KEY: edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b" \
    -F file=@README.csv http://localhost:8000/upload/

Upload via AJAX
---------------

::

    curl -H "PANDA_USERNAME: panda" -H "PANDA_API_KEY: edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b" \
    --data-binary @test.csv -H "X-Requested-With:XMLHttpRequest" http://localhost:8000/upload/?qqfile=test.csv

Categories
==========

Categories are identified by slug, rather than by integer id (though they do have one).

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

Datasets are identified by slug, rather than by integer id (though they do have one).

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

The Dataset list endpoint also provides full-text search over datasets' metadata via the ``q`` parameter.

.. note::

    By default search results are complete Dataset objects, however, it's frequently useful to return simplified objects for rendering lists, etc. To return simplified objects just add ``simple=true`` to the query.

::

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

Data
========

Data objects are referenced by `UUIDs <http://en.wikipedia.org/wiki/Universally_unique_identifier>`_. They do not have a unique integer id. Furthermore, Data objects are accessible at **two** separate endpoints, a global endpoint at ``/api/1.0/data/`` and a per-dataset endpoint at ``/api/1.0/dataset/[slug]/data/``. There are some slight differences in how these endpoints function, which are detailed below.

.. warning::

    Due to the nuances of implementing an API over Solr, this endpoint differs in significant ways from a "normal" Tastypie API endpoint. Please read this documentation carefully.

Schema
------

Schema is only accessible at the global endpoint::

    http://localhost:8000/api/1.0/data/schema/

List
----

Using the global endpoint will list all data in PANDA. The response is a ``meta`` object with paging information and an ``objects`` array containing simplified **Dataset** objects, each of which contains its own ``meta`` object and an ``objects`` array containing **Data** objects. The Datasets group the Data objects.

When using this endpoint the ``limit`` and ``offset`` parameters refer to the groups returned. If you wish to paginate the result sets of each dataset you can use ``group_limit`` and ``group_offset`` although this is typically not the behavior a user would expect.

::

    http://localhost:8000/api/1.0/data/

Using the per-dataset endpoint will return a single simplified **Dataset** object (not an array) with an embedded ``meta`` object and an embedded ``objects`` array containing **Data** objects. Only the Data from a single dataset will be returned.

::

    http://localhost:8000/api/1.0/dataset/[slug]/data/
    
Search
------

The list endpoint is overloaded to provide full-text search via the ``q`` parameter::

    http://localhost:8000/api/1.0/data/?q=[query]

For a single dataset::

    http://localhost:8000/api/1.0/dataset/[slug]/data/?q=[query]

Fetch
-----

Any Data::

    http://localhost:8000/api/1.0/data/[uuid]/

Only Data within a single dataset (will return a ``404`` if you request a UUID which belongs to another Dataset)::

    http://localhost:8000/api/1.0/dataset/[slug]/data/[uuid]/

Create
------

To create a new Data object, send an HTTP ``POST`` request to the list endpoint with the new object in the body. An example object::

    {
        'data': [
            'column A value',
            'column B value',
            'column C value'
        ],
        dataset: '/api/1.0/dataset/[slug]/'
    }

When using the global list endpoint you must include the dataset attribute, however, if posting to a per-dataset list endpoint you may omit it.

Update
------

Update functions similarly to create, however you must use the HTTP ``PUT`` verb and you must send your requests to a specific Data object, such ``/api/1.0/data/[uuid]`` or ``/api/1.0/dataset/[slug]/data/[uuid]``. This will delete the existing object and replace with the one you've sent, reusing the same UUID. If you want to maintain the row number of the original object (if any), you must include it in the request, e.g.::

    {
        'data': [
            ...
        ],
        row: 42
    }

Bulk create
-----------

To create objects in bulk you may ``PUT`` a an array of objects to either the global or a per-dataset endpoint.

.. note::

    This action differs from both normal Tastypie behavior and the REST standard. It may change in the future.

Delete
------

TODO

Delete all data from a dataset
------------------------------

TODO


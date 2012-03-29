=================
API Documentation
=================


The PANDA application is built on top of a REST API that can be used to power custom applications or import/export data in novel ways.

The PANDA API follows the conventions of `Tastypie <https://github.com/toastdriven/django-tastypie>`_ except in important cases where doing so would create unacceptable limitations. If this documentation seems incomplete, refer to Tastypie's page on `Interacting with the API <http://django-tastypie.readthedocs.org/en/latest/interacting.html>`_ to become familiar with the common idiom.

.. note::

    You will probably want to try these URLs in your browser. In order to make them work you'll need to use the ``format``, ``email``, and ``api_key`` query string parameters. For example, to authenticate as the default administrative user that comes with PANDA, append the following query string to any url described on this page::

        ?format=json&email=panda@pandaproject.net&api_key=edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b

Unless otherwise specified, all endpoints that return lists support the ``limit`` and ``offset`` parameters for pagination. Pagination information is contained in the embedded ``meta`` object within the response.

Users
=====

User objects can be queried to retrieve information about PANDA users, however, passwords and API keys are not included in responses.

Example User object:

.. code-block:: javascript

    {
        date_joined: "2011-11-04T00:00:00",
        email: "panda@pandaproject.net",
        first_name: "Redd",
        id: "1",
        is_active: true,
        last_login: "2011-11-04T00:00:00",
        last_name: "",
        resource_uri: "/api/1.0/user/1/"
    }

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

To create a new user, POST a JSON document containing at least the ``email`` property to http://localhost:8000/api/1.0/user/. Other properties such as ``first_name`` and ``last_name`` may also be set. If a ``password`` property is specified it will be set on the new user, but it will not be included in the response. If ``password`` is omitted the user will need to set a password before they can log in (not yet implemented).

Tasks
=====

The Task API allows you to access data about import, export and reindexing processes running on PANDA. This data is read-only.

Example Task object:

.. code-block:: javascript

    {
        end: "2011-12-12T15:11:25",
        id: "1",
        message: "Import complete",
        resource_uri: "/api/1.0/task/1/",
        start: "2011-12-12T15:11:25",
        status: "SUCCESS",
        task_name: "panda.tasks.import.csv",
        traceback: null
    }

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

Data Uploads
============

Due to limitations in upload file-handling, it is not possible to create Uploads via the normal API. Instead data files should be uploaded to http://localhost:8000/data_upload/ either as form data or as an AJAX request. Examples of how to upload files with curl are at the end of this section.

Example DataUpload object:

.. code-block:: javascript

    {
        columns: [
            "id",
            "first_name",
            "last_name",
            "employer"
        ],
        creation_date: "2012-02-08T17:50:09",
        creator: {
            date_joined: "2011-11-04T00:00:00",
            email: "user@pandaproject.net",
            first_name: "User",
            id: "2",
            is_active: true,
            last_login: "2012-02-08T22:45:28",
            last_name: "",
            resource_uri: "/api/1.0/user/2/"
        },
        data_type: "csv",
        dataset: "/api/1.0/dataset/contributors/",
        dialect: {
            delimiter: ",",
            doublequote: false,
            lineterminator: "
            ",
            quotechar: """,
            quoting: 0,
            skipinitialspace: false
        },
        encoding: "utf-8",
        filename: "contributors.csv",
        id: "1",
        imported: true,
        original_filename: "contributors.csv",
        resource_uri: "/api/1.0/data_upload/1/",
        sample_data: [
            [
                "1",
                "Brian",
                "Boyer",
                "Chicago Tribune"
            ],
            [
                "2",
                "Joseph",
                "Germuska",
                "Chicago Tribune"
            ],
            [
                "3",
                "Ryan",
                "Pitts",
                "The Spokesman-Review"
            ],
            [
                "4",
                "Christopher",
                "Groskopf",
                "PANDA Project"
            ]
        ],
        size: 168
    }

Schema
------

::

    http://localhost:8000/api/1.0/data_upload/schema/

List
----

::

    http://localhost:8000/api/1.0/data_upload/

Fetch
-----

::

    http://localhost:8000/api/1.0/data_upload/[id]/

Download original file
----------------------

::

    http://localhost:8000/api/1.0/data_upload/[id]/download/

Upload as form-data
-------------------

When accessing PANDA via curl, your email and API key can be specified with the headers ``PANDA_EMAIL`` and ``PANDA_API_KEY``, respectively::

    curl -H "PANDA_EMAIL: panda@pandaproject.net" -H "PANDA_API_KEY: edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b" \
    -F file=@README.csv http://localhost:8000/data_upload/

Upload via AJAX
---------------

::

    curl -H "PANDA_EMAIL: panda@pandaproject.net" -H "PANDA_API_KEY: edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b" \
    --data-binary @test.csv -H "X-Requested-With:XMLHttpRequest" http://localhost:8000/data_upload/?qqfile=test.csv

.. note::

    When using either upload method you may specify the character encoding of the file by passing it as a parameter, e.g. ``?encoding=latin1``

Related Uploads
===============

Due to limitations in upload file-handling, it is not possible to create Uploads via the normal API. Instead related files should be uploaded to http://localhost:8000/related_upload/ either as form data or as an AJAX request. Examples of how to upload files with curl are at the end of this section.

Example RelatedUpload object:

.. code-block:: javascript

    {
        creation_date: "2012-02-08T23:14:35",
        creator: {
            date_joined: "2011-11-04T00:00:00",
            email: "user@pandaproject.net",
            first_name: "User",
            id: "2",
            is_active: true,
            last_login: "2012-02-08T22:45:28",
            last_name: "",
            resource_uri: "/api/1.0/user/2/"
        },
        dataset: "/api/1.0/dataset/master-4/",
        filename: "PANDA.1.png",
        id: "1",
        original_filename: "PANDA.1.png",
        resource_uri: "/api/1.0/related_upload/1/",
        size: 58990
    }

Schema
------

::

    http://localhost:8000/api/1.0/related_upload/schema/

List
----

::

    http://localhost:8000/api/1.0/related_upload/

Fetch
-----

::

    http://localhost:8000/api/1.0/related_upload/[id]/

Download original file
----------------------

::

    http://localhost:8000/api/1.0/related_upload/[id]/download/

Upload as form-data
-------------------

When accessing PANDA via curl, your email and API key can be specified with the headers ``PANDA_EMAIL`` and ``PANDA_API_KEY``, respectively::

    curl -H "PANDA_EMAIL: panda@pandaproject.net" -H "PANDA_API_KEY: edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b" \
    -F file=@README.csv http://localhost:8000/related_upload/

Upload via AJAX
---------------

::

    curl -H "PANDA_EMAIL: panda@pandaproject.net" -H "PANDA_API_KEY: edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b" \
    --data-binary @test.csv -H "X-Requested-With:XMLHttpRequest" http://localhost:8000/related_upload/?qqfile=test.csv

Categories
==========

Categories are identified by slug, rather than by integer id (though they do have one).

Example Category object:

.. code-block:: javascript

    {
        dataset_count: 2,
        id: "1",
        name: "Crime",
        resource_uri: "/api/1.0/category/crime/",
        slug: "crime"
    }

Schema
------

::

    http://localhost:8000/api/1.0/category/schema/

List
----

When queried as a list, a "fake" category named "Uncategorized" will also be returned. This category includes the count of all Datasets not in any other category. It's slug is ``uncategorized`` is 0, but it can only be accessed as a part of the list.

::

    http://localhost:8000/api/1.0/category/

Fetch
-----

::

    http://localhost:8000/api/1.0/category/[slug]/

Datasets
========

Datasets are identified by slug, rather than by integer id (though they do have one).

Example Dataset object:

.. code-block:: javascript

    {
        categories: [ ],
        columns: [
            "id",
            "first_name",
            "last_name",
            "employer"
        ],
        creation_date: "2012-02-08T17:50:11",
        creator: {
            date_joined: "2011-11-04T00:00:00",
            email: "user@pandaproject.net",
            first_name: "User",
            id: "2",
            is_active: true,
            last_login: "2012-02-08T22:45:28",
            last_name: "",
            resource_uri: "/api/1.0/user/2/"
        },
        current_task: {
            creator: "/api/1.0/user/2/",
            end: "2012-02-08T17:50:12",
            id: "1",
            message: "Import complete",
            resource_uri: "/api/1.0/task/1/",
            start: "2012-02-08T17:50:12",
            status: "SUCCESS",
            task_name: "panda.tasks.import.csv",
            traceback: null
        },
        data_uploads: [
            {
                columns: [
                    "id",
                    "first_name",
                    "last_name",
                    "employer"
                ],
                creation_date: "2012-02-08T17:50:09",
                creator: {
                    date_joined: "2011-11-04T00:00:00",
                    email: "user@pandaproject.net",
                    first_name: "User",
                    id: "2",
                    is_active: true,
                    last_login: "2012-02-08T22:45:28",
                    last_name: "",
                    resource_uri: "/api/1.0/user/2/"
                },
                data_type: "csv",
                dataset: "/api/1.0/dataset/contributors/",
                dialect: {
                    delimiter: ",",
                    doublequote: false,
                    lineterminator: "
                    ",
                    quotechar: """,
                    quoting: 0,
                    skipinitialspace: false
                },
                encoding: "utf-8",
                filename: "contributors.csv",
                id: "1",
                imported: true,
                original_filename: "contributors.csv",
                resource_uri: "/api/1.0/data_upload/1/",
                sample_data: [
                    [
                        "1",
                        "Brian",
                        "Boyer",
                        "Chicago Tribune"
                    ],
                    [
                        "2",
                        "Joseph",
                        "Germuska",
                        "Chicago Tribune"
                    ],
                    [
                        "3",
                        "Ryan",
                        "Pitts",
                        "The Spokesman-Review"
                    ],
                    [
                        "4",
                        "Christopher",
                        "Groskopf",
                        "PANDA Project"
                    ]
                ],
                size: 168
            }
        ],
        description: "",
        id: "1",
        initial_upload: "/api/1.0/data_upload/1/",
        last_modification: null,
        last_modified: null,
        last_modified_by: null,
        name: "contributors",
        related_uploads: [ ],
        resource_uri: "/api/1.0/dataset/contributors/",
        row_count: 4,
        sample_data: [
            [
                "1",
                "Brian",
                "Boyer",
                "Chicago Tribune"
            ],
            [
                "2",
                "Joseph",
                "Germuska",
                "Chicago Tribune"
            ],
            [
                "3",
                "Ryan",
                "Pitts",
                "The Spokesman-Review"
            ],
            [
                "4",
                "Christopher",
                "Groskopf",
                "PANDA Project"
            ]
        ],
        slug: "contributors"
    }

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

To create a new Dataset, ``POST`` a JSON document containing at least ``name`` and ``data_upload`` properties to ``/api/1.0/dataset/``. The ``data_upload`` property may be either an embedded Upload object, or a URI to an existing Upload (for example, ``/api/1.0/upload/17/``). Other properties such as ``description`` may also be set.

.. note::

    The slug field is normally read-only. If you need to create a Dataset with a "well known" slug, you may ``PUT`` the document to that slug and it will be created.
    
    For example, if I wanted to create a dataset that I knew would be accessible at ``/api/1.0/dataset/my-slug/``, I could ``PUT`` my JSON document to that URL and it would be created. If a document with this slug already exists it will be overwritten!

Import
------

Begin an import task. Any data previously imported for this dataset will be lost. Returns the original dataset, which will include the id of the new import task::

    http://localhost:8000/api/1.0/dataset/[id]/import/

Data
========

Data objects are referenced by a unicode ``external_id`` property, specified at the time they are created. This property must be unique within a given ``Dataset``, but does not need to be unique globally. Data objects are accessible at per-dataset endpoints (e.g. ``/api/1.0/dataset/[slug]/data/``). There is also a cross-dataset Data search endpoint at ``/api/1.0/data``, however, this endpoint can only be used for search--not for create, update, or delete. (See below for more.)

.. warning::

    The ``external_id`` property of a Data object is the only way it can be accessed through the API. In order to work with Data via the API you must include this property at the time you create it. By default this property is ``null`` and the Data can not be accessed except via search.

An example ``Data`` object with an ``external_id``:

.. code-block:: javascript

    {
        "data": [
            "1",
            "Brian",
            "Boyer",
            "Chicago Tribune"
        ],
        "dataset": "/api/1.0/dataset/contributors/",
        "external_id": "1",
        "resource_uri": "/api/1.0/dataset/contributors/data/1/"
    }

An example ``Data`` object **without** an ``external_id``, note that it also has no ``resource_uri``:

.. code-block:: javascript

    {
        "data": [
            "1",
            "Brian",
            "Boyer",
            "Chicago Tribune"
        ],
        "dataset": "/api/1.0/dataset/contributors/",
        "external_id": null,
        "resource_uri": null
    }

Schema
------

There is no schema endpoint for Data.

List
----

When listing data, PANDA will return a simplified ``Dataset`` object with an embedded ``meta`` object and an embedded ``objects`` array containing ``Data`` objects. The added Dataset metadata is purely for convenience when building user interfaces. 

::

    http://localhost:8000/api/1.0/dataset/[slug]/data/
    
Search
------

Full-text queries function as "filters" over the normal ``Data`` list. Therefore, search results will be in the same format as the list results described above::

    http://localhost:8000/api/1.0/dataset/[slug]/data/?q=[query]

For details on searching Data across all Datasets, see below.

Fetch
-----

To fetch a single ``Data`` from a given ``Dataset``::

    http://localhost:8000/api/1.0/dataset/[slug]/data/[external_id]/

Create and update
-----------------

Because Data is stored in Solr (rather than a SQL database), there is no functional difference between Create and Update. In either case any Data with the same ``external_id`` will be overwritten when the new Data is created. Because of this requests may be either ``POST``'ed to the list endpoint or ``PUT`` to the detail endpoint.

An example POST::

    {
        "data": [
            "column A value",
            "column B value",
            "column C value"
        ],
        "external_id": "id_value"
    }

This object would be ``POST``'ed to::

    http://localhost:8000/api/1.0/dataset/[slug]/data/

An example ``PUT``::

    {
        "data": [
            "new column A value",
            "new column B value",
            "new column C value"
        ]
    }

This object would be ``PUT`` to::

    http://localhost:8000/api/1.0/dataset/[slug]/data/id_value/

Bulk create and update
----------------------

To create or update objects in bulk you may ``PUT`` an array of objects to the list endpoint. Any object with a matching ``external_id`` will be deleted and then new objects will be created. The body of the request should be formatted like::

    {
        "objects": [
            {
                "data": [
                    "column A value",
                    "column B value",
                    "column C value"
                ],
                "external_id": "1"
            },
            {
                "data": [
                    "column A value",
                    "column B value",
                    "column C value"
                ],
                "external_id": "2"
            }
        ]
    }

Delete
------

To delete an object send a ``DELETE`` request to its detail url. The body of the request should be empty.

Delete all data from a dataset
------------------------------

In addition to deleting individual objects, its possible to delete all objects within a dataset, by sending a ``DELETE`` request to the root per-dataset data endpoint. The body of the request should be empty.

::

    http://localhost:8000/api/1.0/dataset/[slug]/data/

Global search
=============

Searching all data functions slightly differently than searching within a single dataset. Global search requests go to their own endpoint::

    http:://localhost:8000/api/1.0/data/?q=[query]

The response is a ``meta`` object with paging information and an ``objects`` array containing simplified ``Dataset`` objects, each of which contains its own ``meta`` object and an ``objects`` array containing ``Data`` objects. **Each Dataset contains a group of matching Data.**

When using this endpoint the ``limit`` and ``offset`` parameters refer to the ``Datasets`` (that is, the **groups**) returned. If you wish to paginate the result sets within each group you can use ``group_limit`` and ``group_offset``, however, this is rarely useful behavior.


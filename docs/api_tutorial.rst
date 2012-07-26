===================
API Import Tutorial
===================


PANDA's API is designed to allow you to programmatically import (and, to a lesser extent, export) data from PANDA. In this tutorial we will show you how you can use the PANDA API to pull data froma web scraper into PANDA.. Our example will be written in Python using the `Requests <python-requests.org>`_ module, but should be easily portable to any language.

.. note:: 

    If you just want to skip to the code, check out all our `API examples <https://github.com/pandaproject/panda/tree/master/api_examples>`_ on Github.

The problem of synchronization 
==============================

Writing a PANDA scraper usually means that you are trying to *synchronize* PANDA with some data source. True synchornization, where all new, changed and deleted rows get replicated to PANDA is often not possible. Because of this it is important to think in advance about how you will design your import process. 

The first question to to ask yourself is if each row of data has a unique id that will allow you to identify it. (A *primary key* in SQL parlance.) In PANDA we call this value the ``external_id``, because it is generated *external* to PANDA. An ``external_id`` could be anything from a row number to a social security number.

If you can provide an ``external_id`` for your data you will be able to read and update your individual rows of data at a unique URL::

    GET http://localhost:8000/api/1.0/dataset/[slug]/data/[external_id]/

If your data doesn't have an ``external_id`` then you won't be able to read or update individual rows of data. (You can still find them via search or delete them in bulk.) In this case the only way to *synchronize* changes between PANDA and your source dataset will be to delete and reimport all rows.

Even if you do have an ``external_id`` you may still need to delete all rows if your source doesn't provide a *changelog*. A changelog is a stream of metadata that describes when rows of data are modified. Without a changelog it will be impossible to tell if a row of data has been *deleted*. (Because, by definition, it won't be there anymore to find out about.) CouchDB is a rare example of a database that provides a changelog. (See our `CouchDB example <https://github.com/pandaproject/panda/blob/master/api_examples/couchdb.py>`_.)

In most cases you will have an ``external_id``, but not a changelog, so you will need to decide if it is important that rows deleted in the source dataset are also deleted in your PANDA. If so, you will need to wipe out all the data before importing the new data.

.. note::

    There is no technical difference between creating and updating a row in PANDA. In either case data will be overwritten if there is a row with a matching ``external_id`` already in the dataset, otherwise a new row will be created.

Our source data
===============

In this tutorial we are going to be scraping the results of a very simple web scraper, `hosted on Scraperwiki <https://scraperwiki.com/scrapers/basic_twitter_scraper_437/>`_, that is aggregating all tweets about the PANDA Project. Because Scraperwiki has an API, we can write a simple script that will allow us to import the results and then run that script as often as we like.

The data we are importing has three simple columns:

* ``text``, the full-text of the tweet.
* ``id``, Twitter's unique id for the tweet.
* ``from_user``, the username of the person who sent the tweet.

Although Twitter doesn't provide a changelog, they do provide a unique ``id``, which we can use as our ``external_id``. We won't be able to track deleted tweets, but in this case that may actually be to our advantage, since deleted tweets can themselves be interesting. So for this data we will take the approach of reimporting all data, but not deleting anything. This will ensure we pick up any new tweets and any changes (though tweets should never change).

Step 1: Getting setup
=====================

Before we get started we are going to need to import the Python standard JSON module, as well as `Requests <python-requests.org>`_. If you don't have requests you can install it with ``pip install requests`` (or ``easy_install requests``).

.. sourcecode:: python

    import json
    import requests

Now we will define some global variables for values we are going to reuse throughout the script. 

.. sourcecode:: python

    # Replace "localhost:8000" with your PANDA's DNS name or IP address
    PANDA_API = 'http://localhost:8000/api/1.0'

    # Replace these parameters with your adminstrator's email and api key
    PANDA_AUTH_PARAMS = {
        'email': 'panda@pandaproject.net',
        'api_key': 'edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b'
    }

    # This will be the slug of the dataset we are creating/updating
    PANDA_DATASET_SLUG = 'twitter-pandaproject'

    # This is the url where the dataset will live, we send our GET/PUT requests here
    PANDA_DATASET_URL = '%s/dataset/%s/' % (PANDA_API, PANDA_DATASET_SLUG)

    # This is the url under which all data for this dataset lives
    PANDA_DATA_URL = '%s/dataset/%s/data/' % (PANDA_API, PANDA_DATASET_SLUG)

    # Change this value to configure how many rows should be sent to PANDA in each batch
    PANDA_BULK_UPDATE_SIZE = 1000

    # This is the url of the Scraperwiki endpoint for our Twitter scraper
    # This was generated from: https://scraperwiki.com/docs/api#sqlite
    SCRAPERWIKI_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsonlist&name=basic_twitter_scraper_437&query=select%20*%20from%20%60swdata%60'

    # These are the three columns in our dataset
    COLUMNS = ['text', 'id', 'from_user']

Next we will define two convenience methods that handle reading from and writing to PANDA. These will save us repeating ourselves each time we need to send an authenticated request to PANDA.

.. sourcecode:: python

    # Wrapper around a GET request
    def panda_get(url, params={}):
        params.update(PANDA_AUTH_PARAMS)
        return requests.get(url, params=params)

    # Wrapper around a PUT request
    def panda_put(url, data, params={}):
        params.update(PANDA_AUTH_PARAMS)
        return requests.put(url, data, params=params, headers={ 'Content-Type': 'application/json' })

Step 2: Creating the dataset
============================

Before we start importing our data we will first check to see if the dataset exists. If it has not yet been created we will create it.

.. sourcecode:: python

    # Attempt to fetch the dataset at its url
    response = panda_get(PANDA_DATASET_URL)

    # If it doesn't exist the response will be a 404 (not found)
    if response.status_code == 404:
        # This is will be serialized as JSON and sent to PANDA to create the dataset
        dataset = {
            'name': 'PANDA Project Twitter Search',
            'description': 'Results of the scraper at <a href="https://scraperwiki.com/scrapers/basic_twitter_scraper_437/">https://scraperwiki.com/scrapers/basic_twitter_scraper_437/</a>.'
        }

        # In addition to the name and description, we also use the "column" querystring parameter
        # to define the dataset's columns. You will always need to do this when creating datasets
        # via the API.
        response = panda_put(PANDA_DATASET_URL, json.dumps(dataset), params={
            'columns': ','.join(COLUMNS),
        })

.. note::

    See also: complete documentation for the `Datasets API <api.html#datasets>`_.

Step 3: Fetching data from Scraperwiki
======================================

To get data from Scraperwiki we simply request the url we defined above. Because we specified the ``jsonlist`` parameter the response is a JSON document containing an array of keys and an array of rows.

.. sourcecode:: python

    # Request the latest data
    response = requests.get(SCRAPERWIKI_URL)

    # The response is json, so deserialize it
    data = json.loads(response.content)

Step 4: Load the data into PANDA!
=================================

Now that we have our data from Scraperwiki we simply iterate over the rows and convert them into batches of data to be sent to PANDA.

.. sourcecode:: python

    # This is the data structure that will be sent to PANDA
    put_data = {
        'objects': []
    }

    # The row data from Scraperwiki is inside the "data" key
    # We enumerate the rows as we go so we can load the data in batches
    for i, row in enumerate(data['data']):
        # Each row we send to PANDA consists of "data", an array of column values
        # and the "external_id", which *must* be unicode
        put_data['objects'].append({
            'data': row,
            'external_id': unicode(row[1])
        })

        # Everytime we've processed 1000 records, we send them to PANDA
        if i and i % PANDA_BULK_UPDATE_SIZE == 0:
            panda_put(PANDA_DATA_URL, json.dumps(put_data))
            put_data['objects'] = []
            
    # At the end we will probably have records left over, so we send the rest
    if put_data['objects']:
        print 'Updating %i rows' % len(put_data['objects'])
        response = panda_put(PANDA_DATA_URL, json.dumps(put_data))

.. note::

    See also: complete documentation for the `Data API <api.html#data>`_.

Step 5: PANDAmonium!
====================

And that's it, we're done! PANDA now has the data. We can run this script as frequently as we like. Existing rows will be overwritten with any changes and new rows will be added. For very large datasets we suggest running these scripts during off hours.

You can see the `complete script on Github <https://github.com/pandaproject/panda/blob/master/api_examples/scraperwiki_twitter.py>`_.


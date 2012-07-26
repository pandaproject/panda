===================
API Import Tutorial
===================


PANDA's API is designed to allow you to programmatically import (and, to a lesser extent, export) data from PANDA. In this tutorial we will show you how you can use the PANDA API to programmaticaly import data from a variety of sources. Our examples will be written in Python using the `Requests <python-requests.org>`_ library, but should be easily portable to any language.

If you just want to skip the code, check out our `API examples <https://github.com/pandaproject/panda/tree/master/api_examples>`_ on Github.

Can my data be updated?
=======================

Before you use the API to import data into PANDA you need to ask yourself if each row of data has a unique id that will allow you to identify it. If you use SQL, you can think of this like the *primary key* for the dataset. In PANDA we call this value the ``external_id``, because it is generated *external* to PANDA. An ``external_id`` could be anything from a row number to a social security number.

If you can provide an ``external_id`` for your data you will be able to read and update your individual rows of data at a unique URL::

    GET http://localhost:8000/api/1.0/dataset/[slug]/data/[external_id]/

If your data doesn't have an ``external_id`` then you won't be able to read or update individual rows of data. (You can still find them via search or make changes in bulk.) In this case the only way to *synchronize* changes between PANDA and your source dataset will be to delete and reimport all rows.

Even if you do have an ``external_id`` you may still need to delete all rows if your source doesn't provide a *changelog*. A changelog is a stream of metadata that describes when rows of data are modified. Without a changelog it will be impossible to tell if a row of data has been *deleted*. CouchDB is an example of a database that provides a changelog. (See our `CouchDB example <https://github.com/pandaproject/panda/blob/master/api_examples/couchdb.py>`_.)

In most cases you will have an ``external_id``, but not a changelog, so you will need to decide if it is important that rows deleted in the source dataset are also deleted in your PANDA. If so, you will need to wipe out all the data before importing the new data.

Our source data
===============

In this tutorial we are going to be scraping the results of a very simple web scraper, `hosted on Scraperwiki <https://scraperwiki.com/scrapers/basic_twitter_scraper_437/>`_, that is aggregating all tweets about the PANDA Project. Because Scraperwiki has an API, we can write a simple script that will allow us to import the results and then run that script as often as we like.



===========================
Local development & testing
===========================

Install basic requirements
==========================

Use the tools appropriate to your operating system to install the following packages. For OSX you can use `Homebrew <https://github.com/mxcl/homebrew>`_. For Ubuntu you can use Apt.

* pip
* virtualenv
* virtualenvwrapper
* PostgreSQL
* Mercurial (hg)

Set up PANDA
============

This script will setup the complete application, *except* for Solr. Be sure to read the comments, as some steps require opening additional terminals:

.. code-block:: bash

    # Get source and requirements
    git clone git://github.com/pandaproject/panda.git
    cd panda
    mkvirtualenv --no-site-packages panda
    pip install -r requirements.txt

    # Create log directory
    sudo mkdir /var/log/panda
    sudo chown $USER /var/log/panda

    # Create data directories
    mkdir /tmp/panda
    mkdir /tmp/panda_exports

    # Enter "panda" when prompted for password
    createuser -d -R -S -P panda
    createdb -O panda panda
    python manage.py syncdb --noinput
    python manage.py migrate --noinput
    python manage.py loaddata panda/fixtures/init_panda.json
    python manage.py loaddata panda/fixtures/test_users.json

    # Start PANDA
    python manage.py runserver

Open a new terminal in the PANDA directory and enter:

.. code-block:: bash

    # Start the task queue 
    workon panda
    python manage.py celeryd

Open *another* terminal in the PANDA directory and enter:

.. code-block:: bash

    # Run a local email server
    workon panda
    fab local_email

Set up Solr
===========

Installing Solr can be tricky and will vary quite a bit depending on your operating system. The following will get you up and running on OSX Lion (and probably other versions). If you've just started the PANDA server, open a new terminal in the PANDA directory and enter these commands:

.. code-block:: bash

    # Get into the env
    workon panda

    # Fetch the Solr 3.4.0 binaries
    curl http://archive.apache.org/dist/lucene/solr/3.4.0/apache-solr-3.4.0.tgz -o apache-solr-3.4.0.tgz
    tar -zxf apache-solr-3.4.0.tgz
    rm apache-solr-3.4.0.tgz

    # Create Solr home directory
    sudo mkdir /var/solr
    sudo chown $USER /var/solr

    # Jump back to the directory where you installed PANDA
    cd ~/src/panda

    # This command will install all Solr configuration
    fab local_reset_solr

    # To start Solr
    fab local_solr

Checking your PANDA
===================

Your PANDA should now be running at::

    http://localhost:8000/

A PANDA installed locally will not run through the normal setup mode procudure. Instead, two default users will be created.

You can login using the default user credentials::

    Username: user@pandaproject.net
    Password: user

Or the default administrator credentials::

    Username: panda@pandaproject.net
    Password: panda

Running Python unit tests
=========================

To run the unit tests, start Solr and execute the test runner, like so:

.. code-block:: bash

    # Ensure you are in the PANDA source directory and your virtualenv is active
    # You may need to customize the fabfile so it can find your Solr installation.
    fab local_solr

    # Quite a bit of output will be printed to the screen. 
    # Wait until you see something like
    # 2011-11-02 14:15:54.061:INFO::Started SocketConnector@0.0.0.0:8983
    # Then, open another terminal and change to your PANDA source directory.
    workon panda
    python manage.py test panda

Running Javascript unit tests
=============================

Running the Javascript unit tests requires that the application server is running (to render the the JST template map). To run the Javascript tests, first start the test server with ``python manage.py runserver``, then open the file ``client/static/js/SpecRunner.html`` in your browser (e.g. ``file://localhost/Users/onyxfish/src/panda/client/static/js/SpecRunner.html``.

Internationalization (I18N)
===========================

PANDA has been "internationalized" so that it can be used by journalists who speak languages other than English. (Because the word internationalization is so long, it is frequently written i18n.)

Generally, PANDA uses Django's `i18n framework <https://docs.djangoproject.com/en/dev/topics/i18n/>`_, which itself uses Python's `gettext <http://docs.python.org/2/library/gettext.html>`_ module. Simplistically, the process is to take every literal text message which would be shown to users and wrap that text in a function call which looks up the appropriate translation for the message. Other Django tools can recognize these function calls and automatically add new messages to the translation files (known as PO files).

A full explanation of how to internationalize an application is beyond the scope of this document, but here are some things developers should know.
* When adding a message in a python file, you must wrap it in a call to ``ugettext``, or one of the related methods.
* When adding a message in a Javascript file, you must wrap it in a call to ``gettext``. 
* When editing messages for clarity or spelling, remember that the literal text is used as the "lookup key" for a translation, so you probably also have to edit the same text wherever it appears in a ``po`` file under the ``locale`` directory.
* Do not add literal messages to Javascript template (``jst``) files, because they won't be detected. Instead, find a matching ``js`` file in ``client/static/js/text`` and add a key/value pair to the dictionary which is returned.
* Special care must be handled with messages which have variable components, or which may have different grammatical forms, for example, singular/plural, depending on the value of a variable. Look for examples elsewhere in the code.

If you make changes or add translated text, you must remember to rebuild the ``po`` files and recompile the messages. This is easily done using fab commands.

.. code-block:: bash
    # To update the PO files with new or edited messages
    fab makemessages

    # after editing the PO files, you must compile them to see the results in a running application
    fab compilemessages

When running locally, if you'd like to see your PANDA running in a different language, create or edit the file ``config/local_settings.py``

.. code-block:: python
    # set the value of language code to an ISO 639-2 language code matching a directory which exists under the locale directory
    LANGUAGE_CODE = 'de'


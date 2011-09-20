PANDA: A Newsroom Data Appliance
================================

PANDA wants to be your newsroom data appliance. It provides a place for you to store data, search it, and share it with the rest of your newsroom.

Take the `PANDA Future Users Survey <http://bit.ly/pandasurvey>`_.

Local development & testing
---------------------------

Requirements:

* pip
* virtualenv
* virtualenvwrapper

Setup script::

    git clone git://github.com/pandaproject/panda.git
    cd panda
    mkvirtualenv --no-site-packages panda
    pip install -r requirements.txt

    # Enter "panda" when prompted for password
    createuser -D -R -S -P panda
    createdb panda
    python manage.py syncdb

Production deployment
---------------------

Coming soon...

AUTHORS
-------

The PANDA board:

* Brian Boyer
* Joe Germuska
* Ryan Pitts

Lead Developer:

* Christopher Groskopf

Contributors:

* Your name here

LICENSE
-------

MIT.


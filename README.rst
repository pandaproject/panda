PANDA: A Newsroom Data Appliance
================================

PANDA wants to be your newsroom data appliance. It provides a place for you to store data, search it, and share it with the rest of your newsroom.

Take the `PANDA Future Users Survey <http://bit.ly/pandasurvey>`_.

Feature list and much more on `the PANDA Project Wiki <https://github.com/pandaproject/panda/wiki>`_.

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
    createdb -O panda panda
    python manage.py syncdb

    python manage.py celeryd

    # In a separate shell
    python manage.py runserver

Production deployment
---------------------

Get hold of an Ubuntu 11.04 server--an EC2 micro based off of ami-1aad5273 works well. SSH into your server and run::

    wget https://raw.github.com/pandaproject/panda/master/setup_panda.sh
    sudo bash setup_panda.sh

You're new panda server should now be serving on port 80. (Ensure port 80 is open in your security group.)

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


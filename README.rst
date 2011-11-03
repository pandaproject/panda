PANDA: A Newsroom Data Appliance
================================

PANDA wants to be your newsroom data appliance. It provides a place for you to store data, search it, and share it with the rest of your newsroom.

Take the `PANDA Future Users Survey <http://bit.ly/pandasurvey>`_.

Feature list and much more on `the PANDA Project Wiki <https://github.com/pandaproject/panda/wiki>`_.

Local development & testing
---------------------------

**Install basic requirements**:

* pip
* virtualenv
* virtualenvwrapper
* PostgreSQL

**Setup PANDA**

This will setup the complete application, *except* for Solr::

    # Get source and requirements
    git clone git://github.com/pandaproject/panda.git
    cd panda
    mkvirtualenv --no-site-packages panda
    pip install -r requirements.txt

    # Create log directory
    sudo mkdir /var/log/panda
    sudo chown $USER /var/log/panda

    # Enter "panda" when prompted for password
    createuser -d -R -S -P panda
    createdb -O panda panda
    python manage.py syncdb --noinput

    # Start the task queue
    python manage.py celeryd

    # Open another terminal
    workon panda
    python manage.py runserver

**Setup Solr**

This part is tricky and will vary quite a bit depending on your operating system. The following instructions will get you up and running on OSX Lion, using `Homebrew <https://github.com/mxcl/homebrew>`_::

    # Install solr 3.4.0
    brew update
    brew install solr

    # Create Solr home directory
    sudo mkdir /var/solr
    sudo chown $USER /var/solr

    # Ensure you are in the PANDA source directory and your virtualenv is active
    # This command will install all Solr configuration
    fab local_reset_solr

**Running unit tests**

To run the unit tests start Solr and execute the test runner, like so::

    # Ensure you are in the PANDA source directory and your virtualenv is active
    fab local_solr

    # Quite a bit of output will be printed to the screen. 
    # Wait until you see something like
    # 2011-11-02 14:15:54.061:INFO::Started SocketConnector@0.0.0.0:8983
    # Then, open another terminal and change to your PANDA source directory.
    workon panda
    python manage.py test redd

Production deployment
---------------------

Get hold of an Ubuntu 11.10 server--an EC2 small based off of ami-a7f539ce works well. SSH into your server and run::

    wget https://raw.github.com/pandaproject/panda/master/setup_panda.sh
    sudo bash setup_panda.sh

Your new PANDA server should now be serving on port 80. (Ensure port 80 is open in your security group.)

AUTHORS
-------

Lead Developer:

* Christopher Groskopf

The PANDA board:

* Brian Boyer
* Joe Germuska
* Ryan Pitts

Contributors:

* Your name here

LICENSE
-------

MIT.


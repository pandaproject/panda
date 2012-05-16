===============================
Installing on your own hardware
===============================

Installation
============

Server requirements
-------------------

PANDA requires a server running `Ubuntu 11.10 <http://www.ubuntu.com/download/server/download>`_. Whether you want to run PANDA in a virtual machine or on the old Compaq under your desk, as long as it can run Ubuntu 11.10, you should be fine. (Performance, of course, may vary widely depending on the hardware.)

Running the install script
--------------------------

SSH into your server and run the following setup commands:

.. code-block:: bash

    wget https://raw.github.com/pandaproject/panda/0.2.0/setup_panda.sh
    sudo bash setup_panda.sh

Note that the setup script **must** be run with sudo.

An installation log will be created at ``/var/log/panda-install.log`` in case you need to review any part of the process.

Checking your PANDA
===================

Your PANDA should now be running and available at port 80. You can visit it either by IP address  or domain name (if you have one configured for your server).

You can login using the default user credentials::

    Username: user@pandaproject.net
    Password: user

Or the default administrator credentials::

    Username: panda@pandaproject.net
    Password: panda


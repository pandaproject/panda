===============================
Installing on your own hardware
===============================

Installation
============

Server requirements
-------------------

PANDA requires a server running `Ubuntu 12.04 <http://www.ubuntu.com/download/server/download>`_. Whether you want to run PANDA in a virtual machine or on the old Compaq under your desk, as long as it can run Ubuntu 12.04, you should be fine. (Performance, of course, may vary widely depending on the hardware.)

Running the install script
--------------------------

SSH into your server and run the following setup commands:

.. code-block:: bash

    wget https://raw.github.com/pandaproject/panda/1.0.3/setup_panda.sh
    sudo bash setup_panda.sh

Note that the setup script **must** be run with sudo.

An installation log will be created at ``/var/log/panda-install.log`` in case you need to review any part of the process.

Setting up your PANDA
=====================

Once the installation is complete your PANDA will be running on port 80 at the public IP address of the server you installed it on.

Your PANDA will be running in setup mode. This guided process will give you an opportunity to configure the time zone and create an administrative user. Once you've completed the setup you will be directed to login to your PANDA with your new administrative user.

You may also wish to configure :doc:`DNS <dns>`, :doc:`E-mail <email>` and/or :doc:`Secure connections (SSL) <ssl>`.


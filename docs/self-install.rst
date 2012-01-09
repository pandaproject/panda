===============================
Installing on your own hardware
===============================

Installation
============

Server requirements
-------------------

PANDA requires a server running Ubuntu 11.10. Whether you want to run PANDA in a virtual machine or on the old Compaq under your desk, as long as it can run Ubuntu 11.10, you should be fine.

TODO: link to Ubuntu download
TODO: document minimum requirements for a performant panda

Running the install script
--------------------------

SSH into your server and run the following setup commands:

.. code-block:: bash

    wget https://raw.github.com/pandaproject/panda/master/setup_panda.sh
    sudo bash setup_panda.sh

Note that the setup script **must** be run with sudo.

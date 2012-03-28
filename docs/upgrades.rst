====================
Upgrading your PANDA
====================

.. note::

    Although we strive to make upgrades as simple as possible, upgrading your PANDA will require that you know how to SSH into your server. If your not technical or you've never done this before, we suggest getting help from someone who has some experience adminstering servers.

0.1.0 to 0.1.1
==============================

To upgrade your PANDA from the first beta release to the 0.1.1 release, SSH into your server and execute the following commands::

    wget https://raw.github.com/pandaproject/panda/master/scripts/migrations/0.1.0-to-0.1.1.sh
    sudo bash 0.1.0-to-0.1.1.sh

Your PANDA will be stopped, the upgrade will be applied and it will then be restarted. A log of this process will be put in ``/var/log/panda-upgrade.log``. 

Check out the :ref:`changelog` to see all the new features and bug fixes in this release!


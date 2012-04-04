====================
Upgrading your PANDA
====================

Before you get started
======================

Although we strive to make upgrades as simple as possible, upgrading your PANDA will require that you know how to SSH into your server. If you need help with this see our guide to :doc:`Connecting with SSH <ssh>`. And don't be afraid to ask for help on the `PANDA Users Group <https://groups.google.com/forum/?fromgroups#!forum/panda-project-users>`_.

0.1.0 to 0.1.1
==============

To upgrade your PANDA from the first beta release to the 0.1.1 release, :doc:`SSH <ssh>` into your server and execute the following commands::

    wget https://raw.github.com/pandaproject/panda/0.1.1/scripts/migrations/0.1.0-to-0.1.1.sh
    sudo bash 0.1.0-to-0.1.1.sh

Your PANDA will be stopped, the upgrade will be applied and it will then be restarted. A log of this process will be put in ``/var/log/panda-upgrade.log``. 

Check out the :ref:`changelog` to see all the new features and bug fixes in this release!

0.1.1 to 0.1.2
==============

To upgrade your PANDA from the first beta release to the 0.1.2 release, :doc:`SSH <ssh>` into your server and execute the following commands::

    wget https://raw.github.com/pandaproject/panda/0.1.2/scripts/migrations/0.1.1-to-0.1.2.sh
    sudo bash 0.1.1-to-0.1.2.sh

Your PANDA will be stopped, the upgrade will be applied and it will then be restarted. A log of this process will be put in ``/var/log/panda-upgrade.log``. 

Check out the :ref:`changelog` to see all the new features and bug fixes in this release!

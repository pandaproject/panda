=================================
Adding more storage to your PANDA
=================================

PANDA stores both raw data files and search indexes. Both of these can be quite large. At some point you may find you need to upgrade your storage for one or both. This document describes how to do this.

.. warning::

    All procedures described on this page **can destroy your data**. Please take every precaution to ensure your data is :doc:`backed up <backups>` before beginning.

Amazon EC2 upgrade
==================

If you are hosting your PANDA on Amazon EC2 and used our :doc:`installation guide <amazon>` then we provide scripts to upgrade your file and index storage. You will need to have at least some experience with administering a server in order to use these scripts.

To upgrade your file storage SSH into your server and execute the following commands::

    cd /opt/panda/scripts
    sudo python migrate_files_volume.py

To upgrade your search index storage the second command would be::

    sudo python migrate_solr_volume.py

Both scripts will prompt you for some information. When asked for your Amazon Access and Secret keys you can paste them into the console. They will not be displayed or logged. You will also need to enter a size (in gigabytes) for your new volume.

Once the script has completed your files or indexes will be on the new volume and your PANDA will be running again.

.. note::

    If you run this script more than once (i.e. migrating from an added volume to a new added volume) then the old volume will not be detached from your instance or destroyed. Describing how to do this is beyond the scope of this documentation.

Self-install upgrade
====================

Although we can't provide a detailed upgrade guide for self-installed PANDA instances, the basic outline of what you need to do is simple:

* Take your PANDA out of service.
* Add a new storage device and mount it at a temporary location.
* Copy the contents of either ``/var/lib/panda`` (for files) or ``/opt/solr/panda/solr`` to the temporary location.
* Unmount the device, delete the original files and remount the device at the original location.
* Restart your PANDA.

Don't forget to update ``/etc/fstab`` so that the new device will be automatically mounted after a reboot.


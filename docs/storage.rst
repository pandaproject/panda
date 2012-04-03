=================================
Adding more storage to your PANDA
=================================

PANDA stores both raw data files and search indexes. Both of these can be quite large. At some point you may find you need to upgrade your storage for one or both. This document describes how to do this.

.. warning::

    All procedures described on this page **can destroy your data**. Please take every precaution to ensure your data is :doc:`backed up <backups>` before beginning.

Amazon EC2 upgrade
==================

If you are hosting your PANDA on Amazon EC2 and used our :doc:`installation guide <amazon>` then adding additional storage is easy. PANDA comes with scripts which will create new storage volumes, attach them to your server, and migrate existing files.

Based on Amazon's defaults for EC2 instances and the size of the PANDA software itself, you need to consider adding storage when you have more than 1.5 GB total data you want to upload. An initial PANDA installation leaves slightly less than 6 GB available storage for files and search indexes. While circumstances vary, search indexes seem to use about three times as much disk space as the uploaded files they index. If you use the :doc:`API<api>` to add data to PANDA, you will use more search index space but not more file storage space.

Before you begin, estimate how much storage you need. Additional storage on Amazon incurs a `monthly cost <http://aws.amazon.com/pricing/ebs/>`_ based on the allocated disk size. If you want to start small, you could simply add an 18GB volume for the search index storage. This would give you capacity for slightly less than 6 GB worth of uploaded files. If you expect to need more than that,  remember that you should allocate at least 3 times more space for your search index volume than for your files volume.

To upgrade your search index storage, :doc:`SSH into your server <ssh>` and execute the following commands::

    cd /opt/panda/scripts
    sudo python migrate_solr_volume.py

To upgrade your file index storage, the second command would be::

    sudo python migrate_files_volume.py

Both scripts will prompt you for some information. When asked for your Amazon Access and Secret keys you can paste them into the console. They will not be displayed or logged. You will also need to enter a size (in gigabytes) for your new volume.

Once the script has completed your files or indexes will be on the new volume and your PANDA will be running again.

.. note::

    If you run this script more than once (i.e. migrating from an added volume to a new added volume) then the old volume will not be detached from your instance or destroyed. Describing how to do this is beyond the scope of this documentation. **You will be billed for EBS volumes until you destroy them, even if they are not actively being used.**

Self-install upgrade
====================

Although we can't provide a detailed upgrade guide for self-installed PANDA instances, the basic outline of what you need to do is simple:

* Take your PANDA out of service.
* Add a new storage device and mount it at a temporary location.
* Copy the contents of either ``/var/lib/panda`` (for files) or ``/opt/solr/panda/solr`` to the temporary location.
* Unmount the device, delete the original files and remount the device at the original location.
* Restart your PANDA.

Don't forget to update ``/etc/fstab`` so that the new device will be automatically mounted after a reboot.


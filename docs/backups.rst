=====================
Backing up your PANDA
=====================

If you are using PANDA in production you will want to ensure that you perform frequent backups. For archival purposes the most crucial thing to store is the data files themselves, however, you will probably also want to backup your search indexes and database.

Amazon EC2 backups
==================

Creating a backup
-----------------

If you are hosting your PANDA on Amazon EC2 then you can make use of EC2's "snapshot" ability for your backups. In essence a snapshot is an exact copy of any EBS volume. You can use this ability to create backups your PANDA server and, if you have :doc:`migrated your files and indexes <storage>`, the volumes they reside on as well. We provide a script to automate this process. You will need to have at least some experience with administering a server in order to use this script.

To perform a one-time backup :doc:`SSH into your server <ssh>` and execute the following commands::

    cd /opt/panda/scripts
    sudo python backup_volumes.py

When asked for your Amazon Access and Secret keys you can paste them into the console. They will not be displayed or logged. Your PANDA will be unavailable during the backup process, which may take some time (especially if your volumes are large).

Once the script has completed your backup will be created and your PANDA will be running again.

Restoring a backup
------------------

Restoring a backup created with snapshots is a matter of restoring each volume and ensuring they are mounted correctly. However, because one of the volumes that will need to be restored is the root volume of the instance, we have to do a little magic. To restore the root volume:

* On the EC2 `Instances tab <https://console.aws.amazon.com/ec2/home?region=us-east-1&#s=Instances>`_ locate the instance you wish to restore.
* Right-click that instance and select "Launch More Like This".
* Proceed through the wizard, modifying the **Instance Type**, if desired.
* Launch your new instance.
* Once the new instance is available, select it and find its instance ID near the top of the bottom pane. It will look like ``i-76acf913``. Note this, you will need it in a minute.
* Right-click on your instance and "Stop" it. (Don't "Terminate" it!)
* Once it's stopped, navigate to the `Volumes tab <https://console.aws.amazon.com/ec2/home?region=us-east-1&#s=Volumes>`_.
* Find the volume which has the instance ID you noted in the "Attachment Information" column.
* Select this volume and click "Detach Volume."
* Once it is detached, delete it.
* On the EC2 `Snapshots tab <https://console.aws.amazon.com/ec2/home?region=us-east-1&#s=Snapshots>`_ locate the latest snapshot of your root volume, in the description it will say "mounted at /". Note the Snapshot ID. It will look like ``snap-f8b6c49f``. You will need this in a moment.
* Select your snapshot and click "Create Volume". Make it 8GB.
* Got back to the `Volumes tab <https://console.aws.amazon.com/ec2/home?region=us-east-1&#s=Volumes>`_. You should see your new volume in the list. Its identifiable by the snapshot ID you noted in the last step.
* Select it and click "Attach Volume".
* Find your instance in the list using the instance ID you noted before. It should still be in "stopped" state. Set the **Device** to ``/dev/sda1``. Attach it!

If you have run either the files or indexes :doc:`storage migration scripts <storage>` then you will also need to restore your additional storage volumes. These are more straight-forward:

* Create a volume from each snapshot in the same manner you created the root volume.
* Make note of the device in the description of each volume. It looks like ``/dev/sdg``.
* When attaching each volume in the instance, use this value as the **Device**.

Once all volumes have been created and attached, navigate back to the  `Instances tab <https://console.aws.amazon.com/ec2/home?region=us-east-1&#s=Instances>`_, find your instance in the list, right-click it and select "Start". Once it is finished booting up you will have successfully restored your PANDA backup!

Self-install backups
====================

If you chose to self-install PANDA your backup options may vary widely. If possible you should consider periodically disabling the PANDA services and backing up the entire filesystem. If you have files and indexes stored on separate devices you will, of course, want to back those up as well. Using compressed and/or incremental backups will likely save you a significant amount of storage space.


=================================
Manually importing large datasets
=================================

When you need to manual import
==============================

The PANDA web interface may fail when you attempt to upload very large datasets. The exact size at which the uploads will fail depends on the specifics of your server (RAM size, in particular), but anything larger than 100MB may be a problem.

If you experience problems uploading large files, this document describes an alternative way of uploading them that bypasses the web interface. This method is much less convenient, but should be accessible for intermediate to advanced PANDA operators. 

Uploading a file to your server
-------------------------------

Manually importing files is a two-step process. First you must upload them to your server, then you can execute the import process.

Uploading files your server requires using a command-line program called ``scp``. This program allows you to send a file to your server over :doc:`SSH <ssh>`. It may help to quickly review the :doc:`SSH <ssh>` documentation now. If you are on Mac/Linux, `scp` comes preinstalled. On Windows it comes as part of `Putty <http://docs.amazonwebservices.com/AWSEC2/latest/UserGuide/putty.html>`_. In either case, the command to upload your file will look like:

``scp -i /path/to/my/ec2_key.pem /path/to/my/dataset.csv ubuntu@my_server_domain_name.com:/var/lib/panda/uploads/``

.. note::

    You should be very careful that the filename you upload to does not already exist. ``scp`` will not warn you before overwriting an existing file. It is a best practice to append the current date to your filename in order to ensure it is unique.

Executing the manul import
--------------------------

Once your file has finished copying to your PANDA server, you will need to SSH in to execute the manual import process. Refer to the :doc:`SSH <ssh>` documentation for instructions on how to SSH in. Once you're at the command line on your server, execute the following commands to import your file:

.. code-block:: bash

    cd /opt/panda/scripts
    manual_import.py dataset_filename.csv user@email.com

In this case ``dataset_filename.csv`` is the name of the file you uploaded and ``user@email.com`` is the login of the user you want the to "own" the dataset.

Once this script returns your file will be importing via the normal process and you can review it's progress via the web interface. The dataset name and description will be set to the system defaults and should be updated in the web interface. From this point forward the dataset should be indistinguishable from one uploaded via the normal process.

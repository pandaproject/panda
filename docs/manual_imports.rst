=================================
Manually importing large datasets
=================================

When you need to manual import
==============================

The PANDA web interface may fail when you attempt to upload very large datasets. The exact size at which the uploads will fail depends on the specifics of your server (RAM size, in particular), but anything larger than 100MB may be a problem. PANDA may also experience issues when re-indexing very large datasets for the purpose of enabling field-level search.

If you experience either of these problems, this document describes an alternative way of uploading data that bypasses the web interface. This method is much less convenient, but should be accessible for intermediate to advanced PANDA operators.

Uploading a file to your server
===============================

Manually importing files is a two-step process. First you must upload them to your server, then you can execute the import process.

Uploading files to your server requires using a command-line program called ``scp``. This program allows you to send a file to your server over :doc:`SSH <ssh>`. It may help to quickly review the :doc:`SSH <ssh>` documentation now. If you are on Mac/Linux, `scp` comes preinstalled. On Windows it comes as part of `Putty <http://docs.amazonwebservices.com/AWSEC2/latest/UserGuide/putty.html>`_. In either case, the command to upload your file will look like:

``scp -i /path/to/my/ec2_key.pem /path/to/my/dataset.csv ubuntu@my_server_domain_name.com:/tmp/``

Executing the manual import
===========================

Once your file has finished copying to your PANDA server, you will need to SSH in to execute the manual import process. Refer to the :doc:`SSH <ssh>` documentation for instructions on how to SSH in. Once you're at the command line on your server, execute the following commands to import your file:

.. code-block:: bash

    sudo mv /tmp/dataset.csv /var/lib/panda/uploads/
    sudo chown panda:panda /var/lib/panda/uploads/dataset.csv
    cd /opt/panda
    sudo -u panda -E python manage.py manual_import dataset.csv user@email.com

.. note::

    ``sudo mv`` will not prompt you before overwriting another file of the same name. You may wish to verify that you do not have another upload with the same name by running ``sudo ls /var/lib/panda/uploads/``.

In the example ``dataset.csv`` is the name of the file you uploaded (not including the path) and ``user@email.com`` is the login of the user you want the to "own" the dataset.

Once this script returns your file will be importing via the normal process and you can review it's progress via the web interface. The dataset name and description will be set to the system defaults and should be updated in the web interface. From this point forward the dataset should be indistinguishable from one uploaded via the normal process.


Enabling field search during bulk load
=======================================

PANDA may have trouble re-indexing "large" datasets, typically of millions of rows or more. Re-indexing is performed when you add field-level search to a dataset after initial import.
If you have trouble re-indexing a large dataset, you can supply the bulk import command with a schema override file that enables field-level search during initial import.

.. code-block:: bash

    sudo mv /tmp/dataset.csv /var/lib/panda/uploads/
    sudo chown panda:panda /var/lib/panda/uploads/dataset.csv
    cd /opt/panda
    sudo -u panda -E python manage.py manual_import dataset.csv user@email.com -o /path/to/schema_overrides.csv


Schema override file format
----------------------------

The schema override file provides the ability to enable field-level search and customize the data types for any combination of fields. The override file should be a simple comma-separated CSV with two columns:

- **field name** (required) must precisely match corresponding field name in source data file (note, match is case sensitive!)
- **data type** (optional) is a valid PANDA data type. Otherwise uses PANDA's defaults:

  - unicode
  - int
  - float
  - bool
  - datetime
  - date
  - time

When defining a schema override file, it's a good idea to test a smaller sample of data to ensure you have the correct column names and data types.
PANDA will often guess the right data type for a column based on a sampling of data. However, this may not always work as expected,
such as a salary field prefixed with a dollar sign (PANDA will treat this as a string rather than interpreting it as a float).

Experimenting with a subset of data will help identify such issues and suggest potential pre-processing steps that might be necessary prior
to final import (e.g. stripping a leading dollar sign from a currency field).

Once you've ironed out such kinks on the smaller data slice, you can apply the schema overrides to the full data set.

Below is a sample data set and schema override file.

.. code-block:: bash

    # my_sample_data.csv
    name,birthdate,salary,zip
    John,1990-01-01,55000,20007
    Jane,1989-01-01,65000,20007

The related schema override file (below) would add indexes on *birthdate*, *salary* and *zip*.

.. code-block:: bash

    # schema_overrides.csv
    birthdate,
    salary,
    zip,unicode

In this example, PANDA correctly assigns data types for *birthdate* and *salary*, so we can leave the data type column blank for those fields.
However, we explicitly specify *unicode* for zip code to ensure it is treated as a string rather than an integer.
